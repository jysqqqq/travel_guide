# 实现新功能指南

本文档将指导你如何在项目中系统地实现新功能,包括后端 API 开发和前端集成。

## 目录

1. [后端开发](#1-后端开发)
2. [前端开发](#2-前端开发)
3. [测试流程](#3-测试流程)
4. [部署注意事项](#4-部署注意事项)
5. [最佳实践](#5-最佳实践)
6. [非模型相关的 API 实现](#6-非模型相关的-api-实现)

## 1. 后端开发

### 1.1 创建模型

如果需要新的数据模型,在 `backend/api/models.py` 中定义:

```python
from django.db import models
from django.conf import settings

class YourModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='your_models'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name
```

创建模型后,需要执行数据库迁移:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 1.2 创建序列化器

在 `backend/api/serializers.py` 中创建序列化器:

```python
from rest_framework import serializers
from .models import YourModel

class YourModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YourModel
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
```

### 1.3 创建视图

在 `backend/api/views.py` 中添加视图。有两种主要方式:

#### 方式一: ViewSet (推荐用于标准 CRUD 操作)

```python
from rest_framework import viewsets, permissions
from .models import YourModel
from .serializers import YourModelSerializer

class YourModelViewSet(viewsets.ModelViewSet):
    """
    处理 YourModel 的 CRUD 操作
    """
    serializer_class = YourModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        只返回当前用户的数据
        """
        return YourModel.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        创建时自动关联当前用户
        """
        serializer.save(user=self.request.user)
```

#### 方式二: APIView (适用于自定义操作)

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class YourCustomView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # 处理 GET 请求
        data = self.get_data()
        return Response(data)
    
    def post(self, request):
        # 处理 POST 请求
        serializer = YourModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### 1.4 配置 URL

在 `backend/api/urls.py` 中注册路由:

```python
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'your-models', views.YourModelViewSet, basename='your-model')

urlpatterns = [
    path('', include(router.urls)),
    # 自定义视图的 URL
    path('custom-endpoint/', views.YourCustomView.as_view(), name='custom-endpoint'),
]
```

## 2. 前端开发

### 2.1 定义类型

在 `frontend/smart-travel-guide/types/index.ts` 中定义接口:

```typescript
export interface YourModel {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface YourModelCreateInput {
  name: string;
  description?: string;
}
```

### 2.2 扩展 API 服务

在 `frontend/smart-travel-guide/services/api.ts` 中添加新的 API 方法:

```typescript
import { YourModel, YourModelCreateInput } from '@/types'

export const api = {
  // ... 现有的 API 方法
  yourModel: {
    getAll: async () => {
      const response = await axiosInstance.get<YourModel[]>('/your-models/');
      return response.data;
    },
    
    getById: async (id: number) => {
      const response = await axiosInstance.get<YourModel>(`/your-models/${id}/`);
      return response.data;
    },
    
    create: async (data: YourModelCreateInput) => {
      const response = await axiosInstance.post<YourModel>('/your-models/', data);
      return response.data;
    },
    
    update: async (id: number, data: Partial<YourModelCreateInput>) => {
      const response = await axiosInstance.patch<YourModel>(`/your-models/${id}/`, data);
      return response.data;
    },
    
    delete: async (id: number) => {
      await axiosInstance.delete(`/your-models/${id}/`);
    },
  },
}
```

### 2.3 创建组件

在 `frontend/smart-travel-guide/app/components` 下创建新组件:

```typescript
'use client'

import { useState, useEffect } from 'react'
import { api } from '@/services/api'
import { YourModel } from '@/types'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"

export function YourModelList() {
  const [items, setItems] = useState<YourModel[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const data = await api.yourModel.getAll()
        setItems(data)
      } catch (err) {
        setError('获取数据失败')
        toast.error('获取数据失败')
      } finally {
        setIsLoading(false)
      }
    }

    fetchItems()
  }, [])

  if (isLoading) {
    return <div>加载中...</div>
  }

  if (error) {
    return <div className="text-red-500">{error}</div>
  }

  return (
    <div className="space-y-4">
      {items.map((item) => (
        <Card key={item.id}>
          <CardHeader>
            <CardTitle>{item.name}</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{item.description}</p>
            <div className="mt-4">
              <Button variant="outline" size="sm">
                查看详情
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
```

### 2.4 创建页面

在 `frontend/smart-travel-guide/app` 下创建新页面:

```typescript
// app/your-page/page.tsx
import { YourModelList } from '@/components/your-model-list'

export default function YourPage() {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">你的页面标题</h1>
      <YourModelList />
    </div>
  )
}
```

## 3. 测试流程

### 3.1 后端测试

1. API 端点测试
   - 使用 Postman 或类似工具测试所有端点
   - 检查不同 HTTP 方法的响应
   - 验证权限控制是否正确

2. 数据验证测试
   - 测试必填字段验证
   - 测试字段类型验证
   - 测试业务规则验证

3. 错误处理测试
   - 测试无效输入的响应
   - 测试未授权访问的响应
   - 测试资源不存在的响应

### 3.2 前端测试

1. 组件渲染测试
   - 检查初始渲染是否正确
   - 验证加载状态显示
   - 验证错误状态显示

2. 用户交互测试
   - 测试表单提交
   - 测试按钮点击
   - 测试数据更新

3. 集成测试
   - 测试与后端 API 的交互
   - 测试错误处理
   - 测试用户反馈（如提示消息）

## 4. 部署注意事项

### 4.1 后端部署

1. 数据库迁移
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. 静态文件收集
   ```bash
   python manage.py collectstatic
   ```

3. 环境变量配置
   - 确保所有必要的环境变量已设置
   - 检查数据库连接配置
   - 检查 Django 设置（DEBUG, ALLOWED_HOSTS 等）

### 4.2 前端部署

1. 环境变量
   - 检查 `.env` 文件配置
   - 确保 API 地址正确

2. 构建
   ```bash
   npm run build
   ```

3. 部署检查
   - 检查路由配置
   - 验证静态资源加载
   - 测试 API 连接

## 5. 最佳实践

### 5.1 代码组织

1. 后端代码组织
   - 模型放在 `models.py`
   - 视图放在 `views.py`
   - 序列化器放在 `serializers.py`
   - URL 配置放在 `urls.py`

2. 前端代码组织
   - 组件放在 `components` 目录
   - 页面放在 `app` 目录
   - API 服务放在 `services` 目录
   - 类型定义放在 `types` 目录

### 5.2 命名规范

1. 后端命名
   - 模型类：大驼峰（UserProfile）
   - 视图类：大驼峰（UserProfileViewSet）
   - URL 路径：kebab-case（user-profiles）

2. 前端命名
   - 组件：大驼峰（UserProfileCard）
   - 文件名：kebab-case（user-profile-card.tsx）
   - API 方法：camelCase（getUserProfile）

### 5.3 错误处理

1. 后端错误处理
   ```python
   from rest_framework.exceptions import ValidationError

   def your_method(self):
       try:
           # 业务逻辑
           pass
       except SomeError as e:
           raise ValidationError(detail={'message': str(e)})
   ```

2. 前端错误处理
   ```typescript
   try {
     await api.yourModel.create(data)
     toast.success('创建成功')
   } catch (error) {
     toast.error('操作失败：' + error.message)
     console.error('Error:', error)
   }
   ```

### 5.4 性能优化

1. 后端优化
   - 使用适当的数据库索引
   - 实现缓存机制
   - 优化查询性能

2. 前端优化
   - 实现数据缓存
   - 使用分页加载
   - 优化组件重渲染

## 6. 非模型相关的 API 实现

对于不依赖数据库模型的 API（如调用外部服务、处理文件、转发请求等），我们有以下实现方式：

### 6.1 使用 APIView

```python
# backend/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import requests  # 用于调用外部 API

class AICompletionView(APIView):
    """
    调用 AI 大模型的 API 示例
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        prompt = request.data.get('prompt')
        if not prompt:
            return Response(
                {'error': '请提供 prompt'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # 调用外部 AI API 的示例
            response = requests.post(
                'https://api.ai-service.com/v1/completions',
                json={'prompt': prompt},
                headers={'Authorization': 'Bearer your-api-key'}
            )
            response.raise_for_status()
            
            return Response({
                'result': response.json()['completion']
            })
        except requests.RequestException as e:
            return Response(
                {'error': f'AI 服务调用失败: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

class TextGeneratorView(APIView):
    """
    简单的文本生成 API 示例
    """
    def get(self, request):
        text_type = request.query_params.get('type', 'default')
        
        # 根据不同类型返回不同的文本
        texts = {
            'welcome': '欢迎使用我们的服务！',
            'goodbye': '感谢使用，再见！',
            'default': '这是默认消息'
        }
        
        return Response({
            'message': texts.get(text_type, texts['default'])
        })
```

### 6.2 使用装饰器视图

```python
# backend/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_file(request):
    """
    处理上传文件的 API 示例
    """
    if 'file' not in request.FILES:
        return Response(
            {'error': '请上传文件'},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    uploaded_file = request.FILES['file']
    # 处理文件的逻辑
    result = handle_file(uploaded_file)
    
    return Response({
        'message': '文件处理成功',
        'result': result
    })

@api_view(['GET'])
def get_system_status(request):
    """
    返回系统状态的 API 示例
    """
    return Response({
        'status': 'healthy',
        'version': '1.0.0',
        'current_time': timezone.now()
    })
```

### 6.3 URL 配置

在 `backend/api/urls.py` 中添加这些视图的路由：

```python
from django.urls import path
from . import views

urlpatterns = [
    # ... 其他 URL 配置 ...
    
    # APIView 路由
    path('ai/complete/', views.AICompletionView.as_view(), name='ai-complete'),
    path('text/generate/', views.TextGeneratorView.as_view(), name='text-generate'),
    
    # 装饰器视图路由
    path('files/process/', views.process_file, name='process-file'),
    path('system/status/', views.get_system_status, name='system-status'),
]
```

### 6.4 前端集成

在 `frontend/smart-travel-guide/services/api.ts` 中添加对应的方法：

```typescript
export const api = {
  // ... 其他 API 方法 ...
  
  ai: {
    complete: async (prompt: string) => {
      const response = await axiosInstance.post('/ai/complete/', { prompt });
      return response.data;
    }
  },
  
  text: {
    generate: async (type?: string) => {
      const response = await axiosInstance.get('/text/generate/', {
        params: { type }
      });
      return response.data;
    }
  },
  
  files: {
    process: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axiosInstance.post('/files/process/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    }
  },
  
  system: {
    getStatus: async () => {
      const response = await axiosInstance.get('/system/status/');
      return response.data;
    }
  }
};
```

### 6.5 注意事项

1. **错误处理**
   - 对外部服务调用要做好错误处理
   - 设置合适的超时时间
   - 考虑重试机制

2. **性能考虑**
   - 对耗时操作考虑使用异步任务
   - 适当使用缓存
   - 考虑限流措施

3. **安全性**
   - 保护敏感配置（如 API 密钥）
   - 验证用户输入
   - 控制文件上传大小和类型

## 结语

按照本指南实现新功能时:

1. 先规划 API 设计
2. 实现后端功能
3. 编写前端代码
4. 进行充分测试
5. 最后部署上线

记住要注重代码质量、性能优化和用户体验。定期审查代码,确保符合最佳实践。 