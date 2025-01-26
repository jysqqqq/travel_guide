# ViewSet 视图集常用属性和方法详解

## 完整示例

```python
class AttractionViewSet(viewsets.ModelViewSet):
    """景点视图集"""
    # 1. 基本属性
    queryset = Attraction.objects.all()
    serializer_class = AttractionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    pagination_class = PageNumberPagination

    # 2. 查询集方法
    def get_queryset(self):
        queryset = super().get_queryset()
        destination_id = self.request.query_params.get('destination')
        if destination_id:
            queryset = queryset.filter(destination_id=destination_id)
        return queryset

    # 3. 序列化器方法
    def get_serializer_class(self):
        if self.action == 'list':
            return AttractionListSerializer
        return AttractionDetailSerializer

    # 4. 对象操作方法
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # 5. 自定义动作
    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        attraction = self.get_object()
        Favorite.objects.create(
            user=request.user,
            attraction=attraction
        )
        return Response({'status': 'success'})
```

## 1. 基本属性

### 1.1 queryset
- **功能**：定义视图集操作的基础数据集
- **示例**：`queryset = Attraction.objects.all()`
- **说明**：可以在这里定义基础的查询集，后续可以通过`get_queryset()`方法进行进一步过滤

### 1.2 serializer_class
- **功能**：指定使用的序列化器类
- **示例**：`serializer_class = AttractionSerializer`
- **说明**：决定了如何将模型实例转换为JSON数据，以及如何将JSON数据转换回模型实例

### 1.3 permission_classes
- **功能**：设置访问权限
- **示例**：
```python
permission_classes = [
    permissions.IsAuthenticatedOrReadOnly,  # 读取无需认证，修改需要认证
    IsOwnerOrReadOnly,  # 自定义权限：只有所有者能修改
]
```
- **说明**：控制谁可以访问API端点，可以组合多个权限类

### 1.4 filter_backends
- **功能**：配置过滤和搜索后端
- **示例**：
```python
filter_backends = [
    filters.SearchFilter,  # 搜索功能
    filters.OrderingFilter  # 排序功能
]
```
- **说明**：用于实现数据过滤、搜索和排序功能

### 1.5 search_fields
- **功能**：指定可搜索的字段
- **示例**：`search_fields = ['name', 'description']`
- **说明**：配合SearchFilter使用，定义哪些字段可以被搜索

## 2. 重要方法

### 2.1 get_queryset()
```python
def get_queryset(self):
    # 基础查询集
    queryset = super().get_queryset()
    
    # 添加过滤条件
    if self.request.user.is_authenticated:
        return queryset.filter(
            Q(is_public=True) | Q(created_by=self.request.user)
        )
    return queryset.filter(is_public=True)
```
- **功能**：自定义查询集的获取逻辑
- **常用场景**：
  - 根据用户身份过滤数据
  - 添加查询条件
  - 优化查询性能

### 2.2 get_serializer_class()
```python
def get_serializer_class(self):
    if self.action == 'list':
        return AttractionListSerializer  # 列表使用简化版序列化器
    elif self.action == 'retrieve':
        return AttractionDetailSerializer  # 详情使用完整版序列化器
    return self.serializer_class
```
- **功能**：根据不同操作返回不同的序列化器
- **常用场景**：
  - 列表和详情使用不同的序列化深度
  - 不同操作使用不同的字段集

### 2.3 perform_create()/perform_update()
```python
def perform_create(self, serializer):
    # 保存时自动设置创建者
    serializer.save(created_by=self.request.user)

def perform_update(self, serializer):
    # 更新时的额外操作
    instance = serializer.save()
    cache.delete(f'attraction_{instance.id}')
```
- **功能**：在创建/更新对象时执行额外操作
- **常用场景**：
  - 自动设置字段
  - 发送通知
  - 清除缓存
  - 处理关联数据

## 3. 自定义动作

### 3.1 使用@action装饰器
```python
@action(
    detail=True,  # True表示操作单个对象，False表示操作列表
    methods=['post'],  # 允许的HTTP方法
    permission_classes=[permissions.IsAuthenticated]  # 权限设置
)
def favorite(self, request, pk=None):
    """添加收藏"""
    attraction = self.get_object()
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        attraction=attraction
    )
    return Response({
        'status': 'success',
        'created': created
    })
```
- **参数说明**：
  - `detail`：是否是详情操作
  - `methods`：允许的HTTP方法
  - `permission_classes`：权限设置
  - `url_path`：自定义URL路径
  - `url_name`：URL名称

## 4. 常用属性

### 4.1 action
- **功能**：表示当前的操作类型
- **可能的值**：
  - `list`：列表操作
  - `create`：创建操作
  - `retrieve`：获取详情
  - `update`：更新操作
  - `partial_update`：部分更新
  - `destroy`：删除操作

### 4.2 request
- **功能**：当前的请求对象
- **常用属性**：
  - `request.user`：当前用户
  - `request.query_params`：GET参数
  - `request.data`：POST/PUT数据
  - `request.method`：HTTP方法

### 4.3 format_kwarg
- **功能**：响应格式设置
- **用途**：支持不同的响应格式（JSON/XML等）

## 5. 最佳实践

### 5.1 查询优化详解

#### select_related 和 prefetch_related

1. **select_related**：
   ```python
   # 不使用 select_related 的情况
   def get_queryset(self):
       # 会产生N+1查询问题
       attractions = Attraction.objects.all()
       for attraction in attractions:
           # 每个景点都会产生一个新的数据库查询
           print(attraction.destination.name)
   
   # 使用 select_related 的情况
   def get_queryset(self):
       # 只产生一次查询，通过JOIN获取所有数据
       return Attraction.objects.select_related('destination')
   ```
   - **作用**：用于优化一对一(OneToOne)和多对一(ForeignKey)的关联查询
   - **原理**：通过SQL的JOIN操作一次性获取关联数据
   - **适用场景**：
     - 获取景点时同时需要目的地信息
     - 获取评论时同时需要用户信息
   - **性能提升**：减少数据库查询次数，避免N+1查询问题

2. **prefetch_related**：
   ```python
   # 不使用 prefetch_related 的情况
   def get_queryset(self):
       # 会产生N+1查询问题
       destinations = Destination.objects.all()
       for destination in destinations:
           # 每个目的地都会产生一个新的数据库查询
           print(destination.attractions.count())
   
   # 使用 prefetch_related 的情况
   def get_queryset(self):
       # 只产生两次查询：一次查询目的地，一次查询所有相关景点
       return Destination.objects.prefetch_related('attractions')
   ```
   - **作用**：用于优化一对多(OneToMany)和多对多(ManyToMany)的关联查询
   - **原理**：分别查询主表和关联表，然后在Python中进行数据关联
   - **适用场景**：
     - 获取目的地时同时需要其所有景点
     - 获取用户时同时需要其所有收藏
   - **性能提升**：将多次查询优化为固定次数的查询

3. **组合使用示例**：
   ```python
   class DestinationViewSet(viewsets.ModelViewSet):
       def get_queryset(self):
           return Destination.objects.select_related(
               'creator'  # 一对一关系：创建者
           ).prefetch_related(
               'attractions',  # 一对多关系：景点
               'attractions__reviews',  # 景点的评论
               'attractions__favorited_by'  # 景点的收藏者
           )
   ```
   - **说明**：
     - `select_related('creator')`：一次性获取所有目的地及其创建者信息
     - `prefetch_related('attractions')`：预先获取所有相关景点
     - `prefetch_related('attractions__reviews')`：同时预先获取景点的评论
   - **性能对比**：
     - 未优化：可能产生数百次查询
     - 优化后：只产生4次查询（目的地、创建者、景点、评论）

4. **注意事项**：
   - 不要过度使用，只预加载需要的关联数据
   - 考虑数据量大小，某些情况下可能需要分页处理
   - 在列表视图和详情视图可能需要不同的优化策略

### 5.2 权限控制详解

1. **内置权限类**：
   ```python
   class DestinationViewSet(viewsets.ModelViewSet):
       permission_classes = [
           permissions.IsAuthenticatedOrReadOnly,  # 读取无需认证，修改需要认证
           permissions.DjangoModelPermissions,     # Django模型权限
       ]
   ```
   - **常用权限类**：
     - `IsAuthenticated`: 必须登录
     - `IsAuthenticatedOrReadOnly`: 读取无需认证，修改需要认证
     - `DjangoModelPermissions`: 使用Django的模型权限系统
     - `IsAdminUser`: 仅管理员可访问

2. **自定义权限类**：
   ```python
   class IsOwnerOrReadOnly(permissions.BasePermission):
       def has_object_permission(self, request, view, obj):
           # 读取请求总是允许
           if request.method in permissions.SAFE_METHODS:
               return True
           # 写入请求需要是对象的所有者
           return obj.user == request.user
   ```
   - **使用场景**：
     - 基于对象所有权的权限控制
     - 基于用户角色的权限控制
     - 基于业务规则的权限控制

### 5.3 错误处理详解

1. **异常处理**：
   ```python
   from rest_framework.exceptions import ValidationError, NotFound

   class AttractionViewSet(viewsets.ModelViewSet):
       def get_object(self):
           try:
               return super().get_object()
           except Http404:
               raise NotFound('景点不存在')

       def perform_create(self, serializer):
           try:
               serializer.save(created_by=self.request.user)
           except IntegrityError:
               raise ValidationError('创建失败：数据完整性错误')
           except Exception as e:
               logger.error(f'创建景点失败：{str(e)}')
               raise ValidationError('创建失败，请稍后重试')
   ```

2. **自定义响应格式**：
   ```python
   from rest_framework.response import Response
   from rest_framework import status

   class CustomResponseMixin:
       def get_response(self, data=None, message='', status=status.HTTP_200_OK):
           return Response({
               'status': 'success' if status < 400 else 'error',
               'message': message,
               'data': data
           }, status=status)

   class AttractionViewSet(CustomResponseMixin, viewsets.ModelViewSet):
       def create(self, request, *args, **kwargs):
           serializer = self.get_serializer(data=request.data)
           serializer.is_valid(raise_exception=True)
           self.perform_create(serializer)
           return self.get_response(
               data=serializer.data,
               message='景点创建成功'
           )
   ```

### 5.4 代码组织详解

1. **使用Mixin类**：
   ```python
   class LogMixin:
       def perform_create(self, serializer):
           logger.info(f'用户{self.request.user}正在创建新记录')
           super().perform_create(serializer)

   class CacheMixin:
       def get_object(self):
           obj = cache.get(self.get_cache_key())
           if not obj:
               obj = super().get_object()
               cache.set(self.get_cache_key(), obj)
           return obj

   class AttractionViewSet(LogMixin, CacheMixin, viewsets.ModelViewSet):
       pass
   ```

2. **视图集拆分**：
   ```python
   # 基础视图集
   class BaseAttractionViewSet(viewsets.ModelViewSet):
       queryset = Attraction.objects.all()
       serializer_class = AttractionSerializer

   # 公开API视图集
   class PublicAttractionViewSet(BaseAttractionViewSet):
       permission_classes = [permissions.AllowAny]
       
       def get_queryset(self):
           return super().get_queryset().filter(is_public=True)

   # 管理API视图集
   class AdminAttractionViewSet(BaseAttractionViewSet):
       permission_classes = [permissions.IsAdminUser]
       serializer_class = AdminAttractionSerializer
   ```

### 5.5 API文档详解

1. **使用装饰器添加文档**：
   ```python
   from drf_yasg.utils import swagger_auto_schema

   class AttractionViewSet(viewsets.ModelViewSet):
       @swagger_auto_schema(
           operation_summary="创建景点",
           operation_description="创建新的景点信息",
           responses={
               201: AttractionSerializer,
               400: "无效的请求数据",
               403: "没有创建权限"
           }
       )
       def create(self, request, *args, **kwargs):
           return super().create(request, *args, **kwargs)
   ```

2. **自定义API文档**：
   ```python
   class AttractionViewSet(viewsets.ModelViewSet):
       def get_serializer_class(self):
           """
           根据不同的操作返回不同的序列化器
           
           list: 返回简化的序列化器
           retrieve: 返回详细的序列化器
           create/update: 返回带验证的序列化器
           """
           if self.action == 'list':
               return AttractionListSerializer
           elif self.action == 'retrieve':
               return AttractionDetailSerializer
           return AttractionSerializer
   ```

### 5.6 测试最佳实践

1. **单元测试**：
   ```python
   class AttractionViewSetTests(APITestCase):
       def setUp(self):
           self.user = User.objects.create_user(
               username='testuser',
               password='testpass'
           )
           self.client.force_authenticate(user=self.user)

       def test_create_attraction(self):
           data = {
               'name': '测试景点',
               'description': '测试描述'
           }
           response = self.client.post('/api/v1/attractions/', data)
           self.assertEqual(response.status_code, 201)
           self.assertEqual(response.data['name'], data['name'])
   ```

2. **集成测试**：
   ```python
   class AttractionAPITests(APITestCase):
       def test_attraction_workflow(self):
           # 创建景点
           attraction = self.create_attraction()
           
           # 更新景点
           self.update_attraction(attraction)
           
           # 收藏景点
           self.favorite_attraction(attraction)
           
           # 删除景点
           self.delete_attraction(attraction)
   ```

这些最佳实践可以帮助我们：
1. 提高代码质量和可维护性
2. 优化API性能
3. 增强安全性
4. 提供更好的用户体验
5. 便于测试和调试 