from django.core.management.base import BaseCommand
from api.models import Attraction, AttractionImage
from wagtail.images.models import Image
from django.db import transaction

class Command(BaseCommand):
    help = '清空所有景点数据，包括图片'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制删除，不需要确认',
        )

    def handle(self, *args, **options):
        if not options['force']:
            confirm = input('这将删除所有景点和相关图片数据。确定要继续吗？(y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('操作已取消'))
                return

        with transaction.atomic():
            # 获取所有景点相关的图片ID
            image_ids = set()
            
            # 收集景点封面图片
            cover_image_ids = Attraction.objects.exclude(
                cover_image__isnull=True
            ).values_list('cover_image_id', flat=True)
            image_ids.update(cover_image_ids)
            
            # 收集景点其他图片
            other_image_ids = AttractionImage.objects.values_list('image_id', flat=True)
            image_ids.update(other_image_ids)
            
            # 删除景点图片关联
            AttractionImage.objects.all().delete()
            self.stdout.write('已删除景点图片关联')
            
            # 删除景点
            attractions_count = Attraction.objects.count()
            Attraction.objects.all().delete()
            self.stdout.write(f'已删除 {attractions_count} 个景点')
            
            # 删除Wagtail图片
            images_count = len(image_ids)
            Image.objects.filter(id__in=image_ids).delete()
            self.stdout.write(f'已删除 {images_count} 张图片')
            
        self.stdout.write(self.style.SUCCESS('所有景点数据已清空！')) 