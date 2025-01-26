from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django import forms
from django.core.exceptions import ValidationError

class Tag(models.Model):
    """标签模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name="标签名")
    category = models.CharField(max_length=50, verbose_name="标签分类")  # 如"主题"、"季节"等
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"

class Destination(Page):
    """目的地模型"""
    description = RichTextField(verbose_name="描述", blank=True)
    long_description = RichTextField(verbose_name="详细描述", blank=True)
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="封面图片"
    )
    location = models.CharField(max_length=200, verbose_name="位置")
    province = models.CharField(max_length=100, verbose_name="省份", blank=True)
    country = models.CharField(max_length=100, verbose_name="国家", default="中国")
    latitude = models.FloatField(verbose_name="纬度", null=True, blank=True)
    longitude = models.FloatField(verbose_name="经度", null=True, blank=True)
    category = models.CharField(max_length=50, verbose_name="目的地类型", default="景区")  # 城市、景区、国家公园等
    tags = models.ManyToManyField(Tag, blank=True, related_name="destinations", verbose_name="标签")
    best_season = models.CharField(max_length=50, blank=True, verbose_name="最佳旅游季节")
    views_count = models.PositiveIntegerField(default=0, verbose_name="浏览量")
    rating = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        verbose_name="平均评分"
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('long_description'),
        FieldPanel('cover_image'),
        FieldPanel('location'),
        FieldPanel('province'),
        FieldPanel('country'),
        FieldPanel('latitude'),
        FieldPanel('longitude'),
        FieldPanel('category'),
        FieldPanel('tags', widget=forms.CheckboxSelectMultiple),
        FieldPanel('best_season'),
    ]

    class Meta:
        verbose_name = "目的地"
        verbose_name_plural = "目的地"

class Attraction(models.Model):
    """景点模型"""
    name = models.CharField(max_length=200, verbose_name="名称")
    description = RichTextField(verbose_name="描述", blank=True)
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='attractions',
        verbose_name="所属目的地"
    )
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="封面图片"
    )
    location = models.CharField(max_length=200, verbose_name="具体位置")
    latitude = models.FloatField(verbose_name="纬度", null=True, blank=True)
    longitude = models.FloatField(verbose_name="经度", null=True, blank=True)
    opening_hours = models.TextField(verbose_name="开放时间", blank=True)
    ticket_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="门票价格"
    )
    category = models.CharField(max_length=50, verbose_name="景点类型", default="景点")  # 景点、餐厅、购物、住宿等
    tags = models.ManyToManyField(Tag, blank=True, related_name="attractions", verbose_name="标签")
    rating = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        verbose_name="平均评分"
    )
    views_count = models.PositiveIntegerField(default=0, verbose_name="浏览量")
    recommended_duration = models.CharField(max_length=50, blank=True, verbose_name="建议游玩时长")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "景点"
        verbose_name_plural = "景点"
        ordering = ['-created_at']

class Comment(models.Model):
    """评论模型"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="用户"
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comments',
        verbose_name="目的地"
    )
    attraction = models.ForeignKey(
        Attraction,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comments',
        verbose_name="景点"
    )
    content = models.TextField(verbose_name="评论内容")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="评分"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.user.username}的评论"

    def clean(self):
        # 确保评论要么关联到目的地，要么关联到景点，不能两者都有或都没有
        if (self.destination and self.attraction) or (not self.destination and not self.attraction):
            raise ValidationError("评论必须且只能关联到一个目的地或景点")

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = "评论"
        ordering = ['-created_at']

class Itinerary(models.Model):
    """行程模型"""
    title = models.CharField(max_length=200, verbose_name="标题")
    description = RichTextField(verbose_name="描述", blank=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='itineraries',
        verbose_name="创建者"
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='itineraries',
        verbose_name="目的地"
    )
    start_date = models.DateField(verbose_name="开始日期")
    end_date = models.DateField(verbose_name="结束日期")
    is_public = models.BooleanField(default=True, verbose_name="是否公开")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "行程"
        verbose_name_plural = "行程"
        ordering = ['-created_at']

class ItineraryDay(models.Model):
    """行程日程模型"""
    itinerary = models.ForeignKey(
        Itinerary,
        on_delete=models.CASCADE,
        related_name='days',
        verbose_name="所属行程"
    )
    day_number = models.PositiveIntegerField(verbose_name="第几天")
    date = models.DateField(verbose_name="日期")
    note = models.TextField(verbose_name="备注", blank=True)

    def __str__(self):
        return f"{self.itinerary.title} - 第{self.day_number}天"

    class Meta:
        verbose_name = "行程日程"
        verbose_name_plural = "行程日程"
        ordering = ['day_number']
        unique_together = ['itinerary', 'day_number']

class ItineraryItem(models.Model):
    """行程项目模型"""
    day = models.ForeignKey(
        ItineraryDay,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="所属日程"
    )
    attraction = models.ForeignKey(
        Attraction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itinerary_items',
        verbose_name="景点"
    )
    custom_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="自定义地点",
        help_text="如果不是景点，可以填写自定义地点（如餐厅、酒店等）"
    )
    start_time = models.TimeField(verbose_name="开始时间")
    end_time = models.TimeField(verbose_name="结束时间")
    description = models.TextField(verbose_name="描述", blank=True)
    transportation = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="交通方式"
    )

    def __str__(self):
        location = self.attraction.name if self.attraction else self.custom_location
        return f"{self.day} - {location}"

    class Meta:
        verbose_name = "行程项目"
        verbose_name_plural = "行程项目"
        ordering = ['start_time']

class Favorite(models.Model):
    """用户收藏"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name="用户"
    )
    attraction = models.ForeignKey(
        Attraction,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name="收藏的景点"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="收藏时间")
    note = models.TextField(blank=True, verbose_name="收藏备注")

    class Meta:
        verbose_name = "收藏"
        verbose_name_plural = "收藏"
        # 确保用户不能重复收藏同一个景点
        unique_together = ['user', 'attraction']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.attraction.name}"

class AttractionImage(models.Model):
    """景点图片模型"""
    attraction = models.ForeignKey(
        Attraction,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="所属景点"
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name="图片"
    )
    title = models.CharField(max_length=200, blank=True, verbose_name="图片标题")
    description = models.TextField(blank=True, verbose_name="图片描述")
    order = models.PositiveIntegerField(default=0, verbose_name="排序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "景点图片"
        verbose_name_plural = "景点图片"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.attraction.name} - {self.title or '图片'}"
