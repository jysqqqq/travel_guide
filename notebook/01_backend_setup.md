# 智能旅游指南项目开发笔记 - 01 后端搭建

## 0. 项目初始配置

### 0.1 项目创建
```bash
# 创建Wagtail项目
wagtail start travel_guide .
cd travel_guide
```

### 0.2 项目结构
```
travel_guide/
├── backend/                # 后端项目目录
│   ├── api/               # API应用
│   │   ├── models.py      # 数据模型
│   │   ├── serializers.py # 序列化器
│   │   ├── views.py       # 视图
│   │   └── urls.py        # URL配置
│   ├── travel_guide/      # 项目配置目录
│   │   ├── settings/      # 设置文件目录
│   │   │   ├── base.py    # 基础设置
│   │   │   ├── dev.py     # 开发环境设置
│   │   │   └── prod.py    # 生产环境设置
│   │   └── urls.py        # 主URL配置
│   └── manage.py          # Django管理脚本
├── frontend/              # 前端项目目录（待创建）
└── notebook/             # 开发笔记目录
```

### 0.3 关键配置文件

#### settings/base.py
```python
INSTALLED_APPS = [
    'home',
    'search',
    'api',  # 新添加的API应用
    
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',
    
    'modelcluster',
    'taggit',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',  # DRF
    'corsheaders',    # CORS
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS中间件
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

# REST Framework设置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# JWT设置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS设置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
CORS_ALLOW_CREDENTIALS = True

# 数据库设置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# 媒体文件设置
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# 静态文件设置
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
```

#### urls.py
```python
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('api/v1/', include('api.urls')),  # API路由
    path('', include(wagtail_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 配置说明

1. **INSTALLED_APPS配置**：
   - `api`: 我们的自定义API应用
   - `wagtail.*`: Wagtail CMS的核心组件
   - `rest_framework`: Django REST framework用于构建API
   - `corsheaders`: 处理跨域资源共享
   
2. **中间件配置(MIDDLEWARE)**：
   - `corsheaders.middleware.CorsMiddleware`: 必须放在最前面，处理跨域请求
   - `SessionMiddleware`: 处理会话
   - `AuthenticationMiddleware`: 处理用户认证
   - `RedirectMiddleware`: 处理Wagtail的重定向

3. **REST Framework配置**：
   ```python
   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': [
           'rest_framework_simplejwt.authentication.JWTAuthentication',
           'rest_framework.authentication.SessionAuthentication',
           'rest_framework.authentication.BasicAuthentication'
       ],
       'DEFAULT_PERMISSION_CLASSES': [
           'rest_framework.permissions.IsAuthenticatedOrReadOnly',
       ],
       'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
       'PAGE_SIZE': 10
   }
   ```

4. **JWT配置**：
   ```python
   SIMPLE_JWT = {
       'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
       'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
       'ROTATE_REFRESH_TOKENS': False,
       'ALGORITHM': 'HS256',
       'SIGNING_KEY': SECRET_KEY,
       'AUTH_HEADER_TYPES': ('Bearer',),
   }
   ```

5. **CORS配置**：
   ```python
   CORS_ALLOWED_ORIGINS = [
       "http://localhost:3000",
       "http://127.0.0.1:3000"
   ]
   CORS_ALLOW_CREDENTIALS = True
   ```

6. **静态文件和媒体文件配置**：
   ```python
   # 媒体文件（用户上传的文件）
   MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # 文件存储路径
   MEDIA_URL = '/media/'                         # 访问URL前缀

   # 静态文件（CSS、JS等）
   STATIC_ROOT = os.path.join(BASE_DIR, 'static')  # 收集的静态文件路径
   STATIC_URL = '/static/'                         # 访问URL前缀
   ```

7. **URL配置**：
   ```python
   urlpatterns = [
       path('admin/', include(wagtailadmin_urls)),         # Wagtail管理界面
       path('documents/', include(wagtaildocs_urls)),      # Wagtail文档
       path('api/v1/', include('api.urls')),              # 我们的API端点
       path('', include(wagtail_urls)),                   # Wagtail页面
   ]
   ```

这些配置的作用：
1. 实现了前后端分离架构
2. 提供了安全的用户认证机制
3. 允许前端跨域访问API
4. 处理静态资源和上传文件
5. 集成了Wagtail CMS的功能
6. 设置了合理的API访问控制

配置的特点：
- 开发环境友好：包含了调试工具和详细错误信息
- 安全性考虑：使用JWT进行认证，设置了CORS限制
- 可扩展性：模块化的设计便于后续添加新功能
- 维护性：清晰的文件组织结构和注释

### 0.4 数据库迁移
```bash
# 创建初始迁移
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

## 1. 环境搭建

### 1.1 创建虚拟环境
```bash
# 创建conda环境
conda create -n travel_guide python=3.11
conda activate travel_guide
```

### 1.2 安装依赖
```bash
# 核心依赖
pip install wagtail  # CMS系统
pip install djangorestframework  # REST API框架
pip install django-cors-headers  # 处理跨域请求
pip install djangorestframework-simplejwt  # JWT认证
```

## 2. 数据模型设计

### 2.1 目的地模型 (Destination)
```python
class Destination(Page):
    description = RichTextField(verbose_name="描述", blank=True)
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="封面图片"
    )
    location = models.CharField(max_length=200, verbose_name="位置")
    latitude = models.FloatField(verbose_name="纬度", null=True, blank=True)
    longitude = models.FloatField(verbose_name="经度", null=True, blank=True)
```

### 2.2 景点模型 (Attraction)
```python
class Attraction(models.Model):
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
```

### 2.3 行程模型 (Itinerary)
```python
class Itinerary(models.Model):
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
```

### 2.4 收藏模型 (Favorite)
```python
class Favorite(models.Model):
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
```

## 3. API接口开发

### 3.1 视图集(ViewSet)介绍

ViewSet是Django REST framework提供的一种高级视图类，它自动处理常见的API操作。我们主要使用了以下几种视图集：

1. **ModelViewSet**：
   ```python
   class AttractionViewSet(viewsets.ModelViewSet):
       """景点视图集"""
       queryset = Attraction.objects.all()
       serializer_class = AttractionSerializer
       permission_classes = [permissions.IsAuthenticatedOrReadOnly]

       def get_queryset(self):
           # 支持按目的地筛选景点
           queryset = Attraction.objects.all()
           destination_id = self.request.query_params.get('destination', None)
           if destination_id:
               queryset = queryset.filter(destination_id=destination_id)
           return queryset
   ```
   - 自动提供列表、创建、检索、更新、删除操作
   - 可以通过重写方法自定义行为
   - 支持过滤和查询参数

2. **权限控制视图集**：
   ```python
   class ItineraryViewSet(viewsets.ModelViewSet):
       """行程视图集"""
       serializer_class = ItinerarySerializer
       permission_classes = [permissions.IsAuthenticatedOrReadOnly]

       def get_queryset(self):
           # 用户只能看到自己的行程和公开的行程
           if self.request.user.is_authenticated:
               return Itinerary.objects.filter(
                   Q(user=self.request.user) | Q(is_public=True)
               )
           return Itinerary.objects.filter(is_public=True)

       def perform_create(self, serializer):
           # 创建时自动设置用户
           serializer.save(user=self.request.user)
   ```
   - 实现了基于用户的权限控制
   - 自动关联当前用户
   - 支持公开和私有数据的区分

3. **自定义动作视图集**：
   ```python
   class DestinationViewSet(viewsets.ModelViewSet):
       """目的地视图集"""
       queryset = Destination.objects.all()
       serializer_class = DestinationSerializer
       permission_classes = [permissions.IsAuthenticatedOrReadOnly]

       @action(detail=True)
       def attractions(self, request, pk=None):
           """获取目的地下的所有景点"""
           destination = self.get_object()
           attractions = destination.attractions.all()
           serializer = AttractionSerializer(attractions, many=True)
           return Response(serializer.data)
   ```
   - 使用@action装饰器添加自定义端点
   - 支持额外的业务逻辑
   - 可以定义GET或POST等不同类型的动作

### 3.2 视图集的使用方法

1. **基本CRUD操作**：
   ```python
   # GET /api/v1/attractions/         # 列表
   # POST /api/v1/attractions/        # 创建
   # GET /api/v1/attractions/{id}/    # 检索
   # PUT /api/v1/attractions/{id}/    # 更新
   # DELETE /api/v1/attractions/{id}/ # 删除
   ```

2. **过滤和搜索**：
   ```python
   # GET /api/v1/attractions/?destination=1  # 获取特定目的地的景点
   # GET /api/v1/attractions/?search=故宫    # 搜索景点（需要配置搜索后端）
   ```

3. **自定义动作**：
   ```python
   # GET /api/v1/destinations/{id}/attractions/  # 获取目的地的景点列表
   ```

4. **分页**：
   ```python
   # GET /api/v1/attractions/?page=2   # 获取第二页数据
   # 返回格式：
   {
       "count": 100,           # 总数
       "next": "URL",          # 下一页URL
       "previous": "URL",      # 上一页URL
       "results": [...]        # 当前页数据
   }
   ```

### 3.3 视图集的最佳实践

1. **查询优化**：
   ```python
   class AttractionViewSet(viewsets.ModelViewSet):
       def get_queryset(self):
           return Attraction.objects.select_related(
               'destination'
           ).prefetch_related(
               'favorited_by'
           )
   ```
   - 使用select_related减少数据库查询
   - 使用prefetch_related处理多对多关系

2. **权限控制**：
   ```python
   class FavoriteViewSet(viewsets.ModelViewSet):
       permission_classes = [permissions.IsAuthenticated]
       
       def get_queryset(self):
           return Favorite.objects.filter(user=self.request.user)
   ```
   - 确保用户只能访问自己的数据
   - 实现细粒度的权限控制

3. **序列化器的选择**：
   ```python
   class ItineraryViewSet(viewsets.ModelViewSet):
       def get_serializer_class(self):
           if self.action == 'list':
               return ItineraryListSerializer  # 简化的序列化器
           return ItineraryDetailSerializer    # 详细的序列化器
   ```
   - 根据不同操作使用不同的序列化器
   - 优化API响应大小

4. **错误处理**：
   ```python
   from rest_framework.exceptions import ValidationError

   class AttractionViewSet(viewsets.ModelViewSet):
       def perform_create(self, serializer):
           try:
               serializer.save()
           except Exception as e:
               raise ValidationError(detail=str(e))
   ```
   - 提供清晰的错误信息
   - 统一的错误处理机制
