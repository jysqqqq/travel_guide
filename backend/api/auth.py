from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password, get_password_validators
from django.conf import settings

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    # 验证必填字段
    if not username or not password or not email:
        return Response(
            {'detail': '请提供用户名、密码和邮箱'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 验证用户名是否存在
    if User.objects.filter(username=username).exists():
        return Response(
            {'username': ['用户名已存在']},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 验证邮箱是否已被注册
    if User.objects.filter(email=email).exists():
        return Response(
            {'email': ['邮箱已被注册']},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 验证密码强度
    try:
        validate_password(password)
    except ValidationError as e:
        # 获取验证器配置的中文错误信息
        validators = get_password_validators(settings.AUTH_PASSWORD_VALIDATORS)
        error_messages = []
        for validator in validators:
            try:
                validator.validate(password)
            except ValidationError as error:
                if hasattr(validator, 'message'):
                    error_messages.append(validator.message)
                else:
                    error_messages.extend(error.messages)
        
        return Response(
            {'password': error_messages},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # 创建用户
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # 返回成功响应
        return Response(
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'detail': '注册成功'
            },
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        return Response(
            {'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }) 