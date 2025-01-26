import requests
import json
import random
import string

BASE_URL = 'http://127.0.0.1:8000/api/v1'

def generate_random_username(length=8):
    """生成随机用户名"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def register_user(username, email, password):
    """注册新用户"""
    response = requests.post(
        f'{BASE_URL}/auth/register/',
        json={
            'username': username,
            'email': email,
            'password': password
        }
    )
    return response.json()

def get_token(username, password):
    """获取JWT令牌"""
    response = requests.post(
        f'{BASE_URL}/auth/token/',
        json={'username': username, 'password': password}
    )
    return response.json()

def print_response(response):
    """打印响应的详细信息"""
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容: {response.text}")
    try:
        print("JSON内容:", json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print("响应不是有效的JSON格式")

def test_favorites(token):
    """测试收藏功能"""
    headers = {'Authorization': f'Bearer {token}'}
    
    # 1. 获取收藏列表
    print("\n1. 获取收藏列表:")
    response = requests.get(f'{BASE_URL}/favorites/', headers=headers)
    print_response(response)
    
    # 2. 添加收藏
    print("\n2. 添加收藏:")
    data = {
        'attraction': 1,  # 假设ID为1的景点存在
        'note': '这个景点看起来不错!'
    }
    response = requests.post(f'{BASE_URL}/favorites/', json=data, headers=headers)
    print_response(response)
    
    if response.status_code == 201:  # 创建成功
        # 获取新创建的收藏ID
        favorite_id = response.json()['id']
        
        # 3. 更新收藏备注
        print("\n3. 更新收藏备注:")
        data = {'note': '更新后的备注'}
        response = requests.patch(
            f'{BASE_URL}/favorites/{favorite_id}/',
            json=data,
            headers=headers
        )
        print_response(response)
        
        # 4. 删除收藏
        print("\n4. 删除收藏:")
        response = requests.delete(
            f'{BASE_URL}/favorites/{favorite_id}/',
            headers=headers
        )
        print(f"删除状态码: {response.status_code}")

if __name__ == '__main__':
    # 生成随机用户名
    username = generate_random_username()
    
    # 注册新用户
    print("注册新用户:")
    user_data = register_user(username, f'{username}@example.com', 'testpassword123')
    print(json.dumps(user_data, indent=2, ensure_ascii=False))
    
    # 使用新用户登录
    token_data = get_token(username, 'testpassword123')
    if 'access' in token_data:
        test_favorites(token_data['access'])
    else:
        print("获取令牌失败:", token_data) 