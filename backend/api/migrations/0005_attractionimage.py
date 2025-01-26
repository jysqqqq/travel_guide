# Generated by Django 5.1.4 on 2025-01-05 02:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_tag_attraction_category_attraction_rating_and_more'),
        ('wagtailimages', '0027_image_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttractionImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, verbose_name='图片标题')),
                ('description', models.TextField(blank=True, verbose_name='图片描述')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='排序')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('attraction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='api.attraction', verbose_name='所属景点')),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailimages.image', verbose_name='图片')),
            ],
            options={
                'verbose_name': '景点图片',
                'verbose_name_plural': '景点图片',
                'ordering': ['order', 'created_at'],
            },
        ),
    ]
