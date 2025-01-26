# JWT 认证实现详解（初学者友好版）

## 1. 什么是 JWT？

JWT（JSON Web Token）是一种用于身份验证的技术，可以理解为一个加密的身份证明。
简单来说：
- JWT 就像一个特殊的通行证
- 服务器给用户一个通行证（token）
- 用户每次访问时都带着这个通行证
- 服务器通过验证通行证来确认用户身份

### 1.1 JWT 的组成部分

一个 JWT token 由三部分组成（用点号分隔）：
1. Header（头部）：包含加密算法等信息
2. Payload（负载）：包含用户信息等数据
3. Signature（签名）：用于验证 token 是否被篡改

例如：
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjM0NX0.7WS8VPF9oyHUVVK9q-j9nbA-qZm0J5PP
```

## 2. 在 Django 中使用 JWT

### 2.1 安装必要的包

```bash
pip install djangorestframework-simplejwt
```

### 2.2 基础配置

```python
# settings.py

# REST framework 设置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# JWT 设置
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # 访问令牌有效期
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # 刷新令牌有效期
    'ROTATE_REFRESH_TOKENS': False,                  # 是否在刷新时更新刷新令牌
    'BLACKLIST_AFTER_ROTATION': True,               # 是否将旧的刷新令牌加入黑名单
    
    'ALGORITHM': 'HS256',                           # 加密算法
    'SIGNING_KEY': SECRET_KEY,                      # 签名密钥
    'AUTH_HEADER_TYPES': ('Bearer',),               # 认证头类型
}
```

### 2.3 配置 URL

```python
# urls.py
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # JWT 认证相关的 URL
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

## 3. JWT 认证流程

让我们通过一个用户登录的例子来理解整个流程：

### 3.1 用户登录获取 Token

```python
# 前端发送登录请求
POST /api/token/
{
    "username": "alice",
    "password": "secretpassword"
}

# 服务器返回
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",  # 访问令牌
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."  # 刷新令牌
}
```

### 3.2 使用 Token 访问 API

```python
# 在请求头中携带 Token
headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGc...'
}

# 发送请求
GET /api/articles/
```

### 3.3 刷新 Token

当访问令牌过期时，使用刷新令牌获取新的访问令牌：

```python
# 发送刷新请求
POST /api/token/refresh/
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# 服务器返回新的访问令牌
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## 4. 实际应用示例

### 4.1 创建用户注册视图

```python
# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
def register(request):
    try:
        # 获取用户信息
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        
        # 创建用户
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        
        # 生成 Token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user_id': user.id,
            'username': user.username,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': '注册失败',
            'detail': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
```

### 4.2 保护视图

```python
# views.py
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

# 方法 1：使用装饰器
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email
    })

# 方法 2：在视图集中设置
from rest_framework import viewsets

class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
```

## 5. 前端使用示例

### 5.1 使用 axios 发送请求

```javascript
// 登录
async function login(username, password) {
    try {
        const response = await axios.post('/api/token/', {
            username,
            password
        });
        
        // 保存 token 到本地存储
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
        
        return response.data;
    } catch (error) {
        console.error('登录失败:', error);
        throw error;
    }
}

// 创建带有认证头的 axios 实例
const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json'
    }
});

// 添加请求拦截器
api.interceptors.request.use(
    config => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// 添加响应拦截器处理 token 过期
api.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;
        
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            
            try {
                // 尝试刷新 token
                const refresh_token = localStorage.getItem('refresh_token');
                const response = await axios.post('/api/token/refresh/', {
                    refresh: refresh_token
                });
                
                // 保存新的 access token
                localStorage.setItem('access_token', response.data.access);
                
                // 重试原始请求
                originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
                return api(originalRequest);
            } catch (refreshError) {
                // 刷新失败，需要重新登录
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                // 重定向到登录页面
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }
        
        return Promise.reject(error);
    }
);
```

## 6. 安全性建议

1. **Token 存储**
   - 永远不要在前端存储敏感信息
   - 使用 HttpOnly Cookie 存储 refresh token
   - access token 可以存储在内存中

2. **Token 有效期**
   - access token 设置较短的有效期（如 15-60 分钟）
   - refresh token 设置较长的有效期（如 1-7 天）

3. **错误处理**
   - 提供清晰的错误信息
   - 不要在错误信息中暴露敏感信息
   - 记录认证失败的日志

4. **其他安全措施**
   - 使用 HTTPS
   - 实现请求频率限制
   - 监控异常登录行为

## 7. 调试技巧

1. **查看 Token 内容**
```python
# 在 Django shell 中：
from rest_framework_simplejwt.tokens import AccessToken

token = "your_token_here"
decoded = AccessToken(token)
print(decoded.payload)  # 查看 token 中的数据
```

2. **测试 Token**
```bash
# 使用 curl 测试
curl -H "Authorization: Bearer your_token_here" http://localhost:8000/api/protected-endpoint/
```

3. **使用 DRF 的调试界面**
   - 访问 API 端点
   - 点击右上角的 "Token" 按钮
   - 输入 token 进行测试

## 8. 常见问题和解决方案

1. **Token 过期处理**
```python
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

try:
    refresh = RefreshToken(refresh_token)
    access_token = str(refresh.access_token)
except TokenError:
    # Token 已过期或无效
    pass
```

2. **自定义 Token 内容**
```python
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 添加自定义信息
        token['username'] = user.username
        token['email'] = user.email
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
```

3. **处理并发请求**
```python
from django.core.cache import cache
from rest_framework.exceptions import Throttled

def get_user_info(request):
    cache_key = f'user_request_{request.user.id}'
    if cache.get(cache_key):
        raise Throttled()
    
    cache.set(cache_key, True, timeout=60)  # 1分钟内限制一次请求
    # 处理请求
```

## 3. JWT 是如何保护视图的？

让我们通过一个具体的例子来理解 JWT 是如何保护视图的：

### 3.1 认证流程详解

1. **用户登录过程**：
```python
# 1. 用户发送登录请求
POST /api/token/
{
    "username": "alice",
    "password": "secretpassword"
}

# 2. 服务器验证用户名密码
# 3. 如果验证成功，生成并返回 token
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

2. **访问受保护视图的过程**：
```python
# 1. 用户发送请求，在请求头中带上 token
GET /api/articles/
Headers: {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGc...'
}

# 2. DRF 的认证中间件会：
# - 检查请求头中是否有 Authorization
# - 验证 token 的有效性
# - 解析 token 获取用户信息
# - 将用户信息附加到 request.user

# 3. 如果 token 无效或过期，返回 401 错误
# 4. 如果 token 有效，继续处理请求
```

### 3.2 保护机制的实现

1. **中间件层面**：
```python
# DRF 的认证中间件会自动处理每个请求
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

2. **视图层面**：
```python
from rest_framework.permissions import IsAuthenticated

# 方法一：使用装饰器保护视图
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # 要求用户必须认证
def protected_view(request):
    # 这里的 request.user 已经是认证过的用户
    return Response({
        'message': f'Hello, {request.user.username}!'
    })

# 方法二：在视图类中设置权限
class ProtectedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # 要求用户必须认证
    
    def list(self, request):
        # request.user 是认证过的用户
        return Response({
            'message': f'Hello, {request.user.username}!'
        })
```

3. **认证过程详解**：
```python
# JWT 认证的简化流程
def jwt_authentication_process(request):
    # 1. 获取 token
    header = request.headers.get('Authorization')
    if not header or not header.startswith('Bearer '):
        raise AuthenticationFailed('No token provided')
    
    token = header.split(' ')[1]
    
    try:
        # 2. 验证 token
        # - 检查签名是否正确
        # - 检查是否过期
        # - 检查其他声明（如果有）
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        
        # 3. 获取用户信息
        user_id = decoded_token['user_id']
        user = User.objects.get(id=user_id)
        
        # 4. 将用户信息附加到请求对象
        request.user = user
        
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')
    except User.DoesNotExist:
        raise AuthenticationFailed('User not found')
```

### 3.3 实际工作流程示例

假设我们有一个博客系统，用户需要登录才能发表文章：

1. **未认证用户尝试访问**：
```python
# 请求
GET /api/articles/create/
# 无 Authorization 头

# 响应
{
    "detail": "Authentication credentials were not provided."
}
```

2. **使用无效 token 访问**：
```python
# 请求
GET /api/articles/create/
Headers: {
    'Authorization': 'Bearer invalid_token'
}

# 响应
{
    "detail": "Token is invalid or expired"
}
```

3. **使用有效 token 访问**：
```python
# 请求
GET /api/articles/create/
Headers: {
    'Authorization': 'Bearer valid_token_here'
}

# 响应
{
    "message": "Welcome to article creation page"
}
```

### 3.4 为什么说 JWT 是安全的？

1. **签名机制**：
- token 包含了签名，使用服务器的密钥生成
- 任何对 token 的篡改都会导致签名验证失败
- 用户无法伪造有效的 token

2. **信息加密**：
- 敏感信息（如密码）永远不会存储在 token 中
- token 中的信息虽然可以解码，但不能被篡改

3. **过期机制**：
- access token 有较短的有效期
- 即使 token 泄露，影响也是有限的

4. **刷新机制**：
- 使用双 token 系统（access + refresh）
- 可以在不要求用户重新登录的情况下更新认证状态
```

## 9. 细粒度的权限控制

JWT 不仅可以用来验证用户身份，还可以结合 Django 的权限系统实现更细粒度的访问控制。

### 9.1 基于用户角色的权限控制

1. **定义用户角色**：
```python
# models.py
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[
        ('admin', '管理员'),
        ('editor', '编辑'),
        ('viewer', '普通用户'),
    ])
```

2. **在 Token 中包含角色信息**：
```python
# serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 将用户角色添加到 token 中
        token['role'] = user.userprofile.role
        return token
```

3. **创建自定义权限类**：
```python
# permissions.py
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # 检查用户是否是管理员
        return request.user.userprofile.role == 'admin'

class IsEditorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # 检查用户是否是编辑或管理员
        return request.user.userprofile.role in ['editor', 'admin']
```

4. **在视图中使用权限类**：
```python
# views.py
from rest_framework import viewsets
from .permissions import IsAdmin, IsEditorOrAdmin

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            # 创建和编辑文章需要编辑或管理员权限
            return [IsEditorOrAdmin()]
        elif self.action == 'destroy':
            # 删除文章需要管理员权限
            return [IsAdmin()]
        # 查看文章允许所有认证用户
        return [permissions.IsAuthenticated()]
```

### 9.2 基于对象级别的权限控制

1. **在模型中添加所有者字段**：
```python
# models.py
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

2. **创建对象级权限类**：
```python
# permissions.py
class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 读取操作允许任何认证用户
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写入操作只允许作者本人
        return obj.author == request.user

class IsAuthorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 检查用户是否是作者或管理员
        return (obj.author == request.user or 
                request.user.userprofile.role == 'admin')
```

3. **在视图中使用对象级权限**：
```python
# views.py
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        # 创建文章时自动设置作者
        serializer.save(author=self.request.user)
```

### 9.3 组合使用多个权限类

```python
# views.py
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    
    def get_permissions(self):
        """
        根据不同的操作返回不同的权限组合
        """
        if self.action == 'list':
            # 查看列表需要基本认证
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'retrieve':
            # 查看详情需要认证并且是作者或管理员
            permission_classes = [permissions.IsAuthenticated, IsAuthorOrAdmin]
        elif self.action in ['create', 'update', 'partial_update']:
            # 创建和编辑需要编辑权限并且是作者
            permission_classes = [IsEditorOrAdmin, IsAuthorOrReadOnly]
        elif self.action == 'destroy':
            # 删除需要管理员权限
            permission_classes = [IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
```

### 9.4 使用装饰器进行权限控制

```python
# views.py
from rest_framework.decorators import api_view, permission_classes

@api_view(['POST'])
@permission_classes([IsAdmin])
def publish_article(request, article_id):
    """只有管理员可以发布文章"""
    article = get_object_or_404(Article, id=article_id)
    article.is_published = True
    article.save()
    return Response({'status': 'published'})

@api_view(['POST'])
@permission_classes([IsEditorOrAdmin])
def feature_article(request, article_id):
    """编辑或管理员可以将文章设为特色"""
    article = get_object_or_404(Article, id=article_id)
    article.is_featured = True
    article.save()
    return Response({'status': 'featured'})
```

### 9.5 动态权限控制

```python
# permissions.py
class HasRequiredRole(permissions.BasePermission):
    def __init__(self, required_roles):
        self.required_roles = required_roles

    def has_permission(self, request, view):
        return request.user.userprofile.role in self.required_roles

# views.py
class ArticleViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action == 'feature':
            # 特定操作需要特定角色
            return [HasRequiredRole(['editor', 'admin'])]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'])
    def feature(self, request, pk=None):
        """将文章设为特色"""
        article = self.get_object()
        article.is_featured = True
        article.save()
        return Response({'status': 'featured'})
```

这样的设计可以让你：
1. 基于用户角色控制访问权限
2. 基于对象所有权控制访问权限
3. 组合多种权限规则
4. 动态调整权限要求
5. 为特定操作设置特定权限

JWT 在这个过程中的作用是：
1. 存储用户身份信息（ID、角色等）
2. 安全传输这些信息
3. 验证用户身份
4. 提供无状态的认证机制
``` 