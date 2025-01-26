from django.core.management.base import BaseCommand
from api.data_collectors.amap_collector import AmapCollector
from api.models import Destination, Attraction, AttractionImage
from django.db import transaction
from api.data_collectors.poi_types import POI_TYPE_MAPPING

class Command(BaseCommand):
    help = '采集目的地的景点、公园、博物馆等观光文化类POI数据'

    def add_arguments(self, parser):
        parser.add_argument('city', type=str, help='要采集的城市名称')
        parser.add_argument('--destination-id', type=int, help='目的地ID')
        parser.add_argument('--max-pages', type=int, default=3, help='每个类型最大采集页数')

    def handle(self, *args, **options):
        city = options['city']
        destination_id = options['destination_id']
        max_pages = options['max_pages']

        # 确保目的地存在
        try:
            destination = Destination.objects.get(id=destination_id)
        except Destination.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'目的地ID {destination_id} 不存在'))
            return

        collector = AmapCollector()
        
        # 采集所有类型的POI数据
        self.stdout.write(f'开始采集 {city} 的观光文化类POI数据...')
        
        total_created = 0
        total_updated = 0
        total_images = 0
        
        for type_code, type_name in POI_TYPE_MAPPING.items():
            self.stdout.write(f'开始采集{type_name}类型的数据...')
            
            # 采集当前类型的POI数据
            pois = collector.collect_city_pois(
                city=city,
                type_codes=[type_code],
                max_pages=max_pages
            )
            
            if not pois:
                self.stdout.write(self.style.WARNING(f'{type_name}类型未采集到数据'))
                continue
                
            self.stdout.write(f'采集到 {len(pois)} 条{type_name}数据')
            
            # 将POI数据保存到数据库
            created_count = 0
            updated_count = 0
            images_count = 0
            
            for poi in pois:
                try:
                    # 先处理图片
                    attraction_data = collector.map_poi_to_attraction(poi, destination.id)
                    other_images = attraction_data.pop('_other_images', [])
                    
                    # 保存景点数据
                    with transaction.atomic():
                        attraction, created = Attraction.objects.update_or_create(
                            name=attraction_data['name'],
                            destination=destination,
                            defaults=attraction_data
                        )
                        
                        # 保存其他图片
                        for image_data in other_images:
                            AttractionImage.objects.create(
                                attraction=attraction,
                                image=image_data['image'],
                                title=image_data['title'],
                                description=image_data['description'],
                                order=image_data['order']
                            )
                            images_count += 1
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                            
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'处理POI数据时出错: {str(e)}'))
                    continue
            
            total_created += created_count
            total_updated += updated_count
            total_images += images_count
            
            self.stdout.write(self.style.SUCCESS(
                f'{type_name}数据导入完成！新建：{created_count}，更新：{updated_count}，图片：{images_count}'
            ))
            
        # 输出总结信息
        self.stdout.write(self.style.SUCCESS(
            f'\n数据采集完成！总计：新建景点：{total_created}，更新景点：{total_updated}，图片：{total_images}'
        )) 