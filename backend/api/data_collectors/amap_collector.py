import requests
import time
from typing import List, Dict, Any, Optional
from django.core.files.base import ContentFile
import io
from PIL import Image as PILImage
from wagtail.images import get_image_model
from .poi_types import POI_TYPE_MAPPING
from django.conf import settings
import hashlib
from django.db import transaction
import os
from django.core.files.images import ImageFile

class AmapCollector:
    """高德地图POI数据采集器"""
    
    def __init__(self):
        self.api_key = settings.AMAP_API_KEY
        self.base_url = 'https://restapi.amap.com/v3/place/text'
        self.Image = get_image_model()
        
    def get_poi_data(self, city: str, type_codes: List[str], page: int = 1) -> Optional[List[Dict[str, Any]]]:
        """获取指定城市和类型的POI数据"""
        params = {
            'key': self.api_key,
            'city': city,
            'types': '|'.join(type_codes),
            'citylimit': 'true',
            'output': 'json',
            'offset': 20,
            'page': page,
            'extensions': 'all'  # 获取详细信息，包括照片
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == '1' and data['pois']:
                return data['pois']
            return None
            
        except Exception as e:
            print(f'获取POI数据时出错: {str(e)}')
            return None
            
    def collect_city_pois(self, city: str, type_codes: List[str], max_pages: int = 3) -> List[Dict[str, Any]]:
        """采集指定城市的所有POI数据"""
        all_pois = []
        page = 1
        
        while page <= max_pages:
            pois = self.get_poi_data(city, type_codes, page)
            if not pois:
                break
                
            all_pois.extend(pois)
            page += 1
            time.sleep(0.5)  # 避免请求过快
            
        return all_pois
        
    def process_image(self, image_url: str, title: str = '') -> Optional[Dict[str, Any]]:
        """处理图片URL，下载并创建Wagtail Image对象"""
        if not image_url:
            return None
            
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            
            # 使用PIL处理图片
            image = PILImage.open(io.BytesIO(response.content))
            
            # 转换为RGB模式（如果是RGBA）
            if image.mode == 'RGBA':
                image = image.convert('RGB')
                
            # 调整图片大小（如果需要）
            max_size = (1200, 1200)
            image.thumbnail(max_size, PILImage.Resampling.LANCZOS)
            
            # 获取图片尺寸
            width, height = image.size
            
            # 保存处理后的图片到临时文件
            temp_filename = f'temp_{title}.jpg'
            temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', temp_filename)
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            image.save(temp_path, format='JPEG', quality=85)
            
            # 创建Wagtail Image对象
            with open(temp_path, 'rb') as f:
                image_file = ImageFile(f, name=temp_filename)
                wagtail_image = self.Image.objects.create(
                    title=title,
                    file=image_file
                )
            
            # 删除临时文件
            os.remove(temp_path)
            
            return {
                'image': wagtail_image,
                'title': title,
                'description': '',
                'order': 0
            }
            
        except Exception as e:
            print(f'处理图片时出错: {str(e)}')
            return None
            
    def map_poi_to_attraction(self, poi: Dict[str, Any], destination_id: int) -> Dict[str, Any]:
        """将POI数据映射为景点数据"""
        # 处理主图片
        cover_image = None
        other_images = []
        
        # 处理所有图片
        if 'photos' in poi and poi['photos']:
            for i, photo in enumerate(poi['photos']):
                image_data = self.process_image(
                    photo.get('url'),
                    title=f"{poi['name']}_{i+1}"
                )
                if image_data:
                    if i == 0:  # 第一张作为封面
                        cover_image = image_data['image']
                    else:  # 其他图片
                        image_data['order'] = i
                        other_images.append(image_data)
        
        # 基本数据映射
        attraction_data = {
            'name': poi['name'],
            'description': poi.get('business', ''),
            'location': poi['address'] or poi['name'],
            'latitude': float(poi['location'].split(',')[1]),
            'longitude': float(poi['location'].split(',')[0]),
            'category': POI_TYPE_MAPPING.get(poi['typecode'], '其他'),
            'destination_id': destination_id,
            'rating': float(poi.get('biz_ext', {}).get('rating', 0)) or 0,
            'views_count': 0
        }
        
        # 如果有封面图片，添加到数据中
        if cover_image:
            attraction_data['cover_image'] = cover_image
            
        # 添加其他图片到数据中
        if other_images:
            attraction_data['_other_images'] = other_images
            
        return attraction_data 