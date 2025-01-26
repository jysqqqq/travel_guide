import time
from typing import Dict, Optional
import re
from django.core.files.base import ContentFile
from wagtail.images import get_image_model
import urllib.parse
import requests
from bs4 import BeautifulSoup

class MafengwoCollector:
    """马蜂窝数据采集器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        }
        self.base_url = 'https://www.mafengwo.cn'
        self.Image = get_image_model()
        
    def get_city_info(self, city_name: str) -> Optional[Dict]:
        """获取城市基本信息"""
        try:
            # 搜索城市
            encoded_city = urllib.parse.quote(city_name)
            search_url = f'{self.base_url}/search/q.php?q={encoded_city}'
            print(f'搜索URL: {search_url}')
            
            # 发送请求
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 解析页面
            soup = BeautifulSoup(response.text, 'html.parser')
            search_div = soup.find('div', class_='search-mdd-wrap')
            
            if not search_div:
                print('未找到搜索结果')
                return None
                
            # 获取城市ID和封面图片
            city_link = search_div.find('a')
            if not city_link:
                print('未找到城市链接')
                return None
                
            href = city_link.get('href', '')
            city_id_match = re.search(r'id=(\d+)', href)
            if not city_id_match:
                print('未找到城市ID')
                return None
                
            # 获取封面图片URL
            style = search_div.get('style', '')
            cover_url_match = re.search(r'url\((.*?)\)', style)
            cover_url = cover_url_match.group(1) if cover_url_match else None
            
            # 创建基本数据结构
            city_data = {
                'title': city_name,
                'description': '',  # 留空
                'location': city_name,
                'category': '城市',
                'best_season': '',  # 留空
                'views_count': 0,
                'rating': 5.0  # 默认值
            }
            
            # 处理封面图片
            if cover_url:
                city_data['cover_image'] = self._process_image(cover_url, city_name)
            
            return city_data
            
        except Exception as e:
            print(f'获取城市信息时出错: {str(e)}')
            return None
            
    def _process_image(self, image_url: str, city_name: str) -> Optional[object]:
        """处理图片"""
        try:
            if not image_url:
                return None
                
            # 清理URL，获取基础URL（去掉所有查询参数）
            clean_url = image_url.split('?')[0].strip('"')
            if not clean_url.startswith('http'):
                clean_url = f'https:{clean_url}'
                
            print(f'处理后的图片URL: {clean_url}')
            
            # 下载图片
            response = requests.get(clean_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 生成文件名
            file_name = f'{city_name}_cover.jpg'
            
            # 创建Wagtail图片
            image_file = ContentFile(response.content, name=file_name)
            wagtail_image = self.Image.objects.create(
                title=f'{city_name}_cover',
                file=image_file
            )
            
            return wagtail_image
            
        except Exception as e:
            print(f'处理图片时出错: {str(e)}')
            return None 