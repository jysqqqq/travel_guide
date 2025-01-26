# DRF 路由管理详解（初学者友好版）

## 1. 什么是路由？

在 Web 开发中，路由就像是一个"交通指挥官"，它负责将用户的请求（比如访问 `http://example.com/users/`）引导到正确的处理函数。
简单来说：
- 当用户访问一个网址时，路由系统决定由哪个函数来处理这个请求
- 路由定义了 URL 和处理函数之间的对应关系

## 2. DRF 的路由系统有什么特别？

Django REST Framework (DRF) 的路由系统特别适合构建 API，因为它：
1. 自动生成标准的 RESTful API 地址
2. 自动处理常见的数据操作（增删改查）
3. 提供了清晰的代码组织方式

### 2.1 一个简单的例子

假设我们要开发一个博客系统的 API，需要管理文章（Article）：

```python
# models.py
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# serializers.py
from rest_framework import serializers

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'created_at']

# views.py
from rest_framework import viewsets

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

# urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register('articles', ArticleViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

这段代码会自动生成以下 API 端点：
- `GET /api/articles/` - 获取所有文章列表
- `POST /api/articles/` - 创建新文章
- `GET /api/articles/1/` - 获取 ID 为 1 的文章详情
- `PUT /api/articles/1/` - 更新 ID 为 1 的文章
- `DELETE /api/articles/1/` - 删除 ID 为 1 的文章

## 3. 路由器（Router）详解

### 3.1 默认路由器（DefaultRouter）

这是最常用的路由器，它提供了完整的功能：

```python
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# 'articles' 是 URL 前缀，ArticleViewSet 是处理这些请求的视图集
router.register('articles', ArticleViewSet)
```

### 3.2 简单路由器（SimpleRouter）

功能较少但更轻量：

```python
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('articles', ArticleViewSet)
```

主要区别：
- DefaultRouter 会生成一个 API 根页面（显示所有可用的 API）
- DefaultRouter 会在 URL 末尾添加斜杠
- SimpleRouter 更简单，没有这些额外功能

## 4. 视图集（ViewSet）类型

### 4.1 ModelViewSet（全功能视图集）

最常用的视图集，提供所有常用操作：

```python
from rest_framework import viewsets

class ArticleViewSet(viewsets.ModelViewSet):
    # 指定要使用的数据
    queryset = Article.objects.all()
    # 指定如何转换数据格式
    serializer_class = ArticleSerializer
```

这相当于传统 Django 中的多个视图函数：
```python
# 传统 Django 方式（需要写很多代码）
def article_list(request):
    if request.method == 'GET':
        # 获取文章列表
        pass
    elif request.method == 'POST':
        # 创建新文章
        pass

def article_detail(request, pk):
    if request.method == 'GET':
        # 获取单个文章
        pass
    elif request.method == 'PUT':
        # 更新文章
        pass
    elif request.method == 'DELETE':
        # 删除文章
        pass
```

### 4.2 ReadOnlyModelViewSet（只读视图集）

当你只需要显示数据，不需要修改数据时使用：

```python
from rest_framework import viewsets

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
```

这只会生成两个 API 端点：
- `GET /articles/` - 获取列表
- `GET /articles/1/` - 获取详情

## 5. 实际案例：博客系统

让我们通过一个完整的博客系统例子来理解：

```python
# models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

# serializers.py
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ArticleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'category', 'category_name', 
                 'created_at', 'is_published']

# views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    
    # 自定义操作：获取某个分类下的所有文章
    @action(detail=True, methods=['get'])
    def category_articles(self, request, pk=None):
        category = self.get_object()
        articles = Article.objects.filter(category=category)
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    # 自定义操作：获取所有已发布的文章
    @action(detail=False, methods=['get'])
    def published(self, request):
        articles = Article.objects.filter(is_published=True)
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('articles', ArticleViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

这个例子会生成以下 API 端点：

基础端点：
- `GET /api/categories/` - 获取所有分类
- `GET /api/articles/` - 获取所有文章
- `POST /api/articles/` - 创建新文章
- `GET /api/articles/1/` - 获取特定文章
- `PUT /api/articles/1/` - 更新特定文章
- `DELETE /api/articles/1/` - 删除特定文章

自定义端点：
- `GET /api/articles/1/category_articles/` - 获取特定分类下的所有文章
- `GET /api/articles/published/` - 获取所有已发布的文章

## 6. 常见问题和解决方案

### 6.1 如何处理嵌套资源？

比如要获取某个分类下的文章：

```python
from rest_framework_nested import routers

# 创建主路由器
router = routers.DefaultRouter()
router.register('categories', CategoryViewSet)

# 创建嵌套路由器
categories_router = routers.NestedDefaultRouter(router, 'categories', lookup='category')
categories_router.register('articles', ArticleViewSet)

# 这会生成类似这样的 URL：
# /api/categories/1/articles/ - 获取分类 1 的所有文章
# /api/categories/1/articles/2/ - 获取分类 1 下的文章 2
```

### 6.2 如何添加权限控制？

```python
from rest_framework import permissions

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    
    # 要求用户登录才能访问
    permission_classes = [permissions.IsAuthenticated]
    
    # 或者自定义权限
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # 列表和详情页面允许所有人访问
            return [permissions.AllowAny()]
        # 其他操作需要登录
        return [permissions.IsAuthenticated()]
```

### 6.3 如何自定义 URL 路径？

```python
from django.urls import path, include

urlpatterns = [
    # API 版本控制
    path('api/v1/', include(router.urls)),
    
    # 自定义认证路径
    path('api/auth/login/', LoginView.as_view()),
    path('api/auth/logout/', LogoutView.as_view()),
]
```

## 7. 最佳实践建议

1. **URL 命名规范**
   - 使用复数形式：`articles` 而不是 `article`
   - 使用小写字母和连字符：`blog-posts` 而不是 `blogPosts`
   - 避免动词，用名词：用 `POST /articles/` 而不是 `/create-article`

2. **视图集组织**
   - 相关功能放在一起
   - 使用清晰的方法名
   - 添加适当的注释

3. **权限控制**
   - 始终设置适当的权限
   - 对敏感操作增加额外的权限检查
   - 记录日志以便追踪问题

4. **错误处理**
   - 返回合适的状态码
   - 提供清晰的错误信息
   - 记录异常以便调试

## 8. 调试技巧

1. **使用 DRF 的浏览器界面**
   访问 API URL 时，DRF 会显示一个友好的界面，可以直接测试 API

2. **查看生成的 URL**
```python
# 在 Django shell 中：
from django.urls import get_resolver
resolver = get_resolver()
for url in resolver.url_patterns:
    print(url.pattern)
```

3. **使用日志调试**
```python
import logging
logger = logging.getLogger(__name__)

class ArticleViewSet(viewsets.ModelViewSet):
    def list(self, request):
        logger.debug(f"Requesting articles with params: {request.query_params}")
        return super().list(request)
``` 