from django.core.management.base import BaseCommand
from api.data_collectors.destination_collector import DestinationCollector
from api.models import Destination
from django.db import transaction
from wagtail.models import Locale, Page
import time

class Command(BaseCommand):
    help = '采集目的地数据'

    def add_arguments(self, parser):
        parser.add_argument('cities', nargs='+', type=str, help='要采集的城市名称列表')
        parser.add_argument(
            '--update',
            action='store_true',
            help='更新已存在的目的地',
        )

    def handle(self, *args, **options):
        collector = DestinationCollector()
        cities = options['cities']
        update = options['update']
        
        # 确保中文 locale 存在
        try:
            locale = Locale.objects.get(language_code='zh')
        except Locale.DoesNotExist:
            locale = Locale.objects.create(language_code='zh')
            
        # 获取首页作为父页面
        try:
            home_page = Page.objects.get(slug='home')
        except Page.DoesNotExist:
            self.stdout.write(self.style.ERROR('未找到首页，请先创建首页'))
            return
        
        total_created = 0
        total_updated = 0
        total_failed = 0
        
        for city in cities:
            self.stdout.write(f'正在采集 {city} 的数据...')
            
            try:
                # 获取城市信息
                city_data = collector.collect_destination_data(city)
                if not city_data:
                    self.stdout.write(self.style.ERROR(f'未找到 {city} 的数据'))
                    total_failed += 1
                    continue
                    
                # 添加必要的字段
                city_data['locale'] = locale
                city_data['slug'] = city
                
                # 保存到数据库
                with transaction.atomic():
                    if update:
                        try:
                            destination = Destination.objects.get(title=city)
                            # 更新字段
                            for key, value in city_data.items():
                                if key not in ['path', 'depth', 'numchild']:  # 排除 Page 模型的特殊字段
                                    setattr(destination, key, value)
                            destination.save()
                            created = False
                        except Destination.DoesNotExist:
                            # 如果不存在，创建新的
                            destination = Destination(**city_data)
                            home_page.add_child(instance=destination)
                            created = True
                    else:
                        if Destination.objects.filter(title=city).exists():
                            self.stdout.write(self.style.WARNING(f'目的地已存在: {city}'))
                            total_failed += 1
                            continue
                            
                        # 创建新的目的地页面
                        destination = Destination(**city_data)
                        home_page.add_child(instance=destination)
                        created = True
                    
                    if created:
                        total_created += 1
                        self.stdout.write(self.style.SUCCESS(f'成功创建目的地: {city}'))
                    else:
                        total_updated += 1
                        self.stdout.write(self.style.SUCCESS(f'成功更新目的地: {city}'))
                            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'处理 {city} 时出错: {str(e)}'))
                total_failed += 1
                continue
                
            # 休息一下，避免请求过快
            time.sleep(2)
            
        # 输出总结
        self.stdout.write('\n采集完成！')
        self.stdout.write(f'新建目的地：{total_created}')
        self.stdout.write(f'更新目的地：{total_updated}')
        self.stdout.write(f'失败：{total_failed}') 