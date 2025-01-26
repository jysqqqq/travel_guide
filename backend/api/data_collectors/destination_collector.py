import json
import requests
from typing import Dict, Optional, Tuple
from .mafengwo_collector import MafengwoCollector

class DestinationCollector:
    """目的地数据收集器，整合马蜂窝图片和 Coze API 数据"""
    
    def __init__(self):
        self.mafengwo_collector = MafengwoCollector()
        self.coze_api_url = "https://api.coze.cn/v1/workflow/stream_run"
        self.coze_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer pat_Q9G6ReJeMkya5l53zyIbZM1neOJ85lrlFYdZIpxpoukYsfk0zLxivMriKEsMTRiS"
        }
        self.workflow_id = "7456427520789332022"
        self.app_id = "7456162824113881129"
        
    def collect_destination_data(self, city_name: str) -> Optional[Dict]:
        """收集目的地数据"""
        try:
            # 获取城市基本信息（包含图片）
            mafengwo_data = self.mafengwo_collector.get_city_info(city_name)
            if not mafengwo_data:
                print(f"从马蜂窝获取 {city_name} 的数据失败")
                return None
                
            # 获取城市详细信息
            coze_data = self._get_coze_data(city_name)
            if not coze_data:
                print(f"从 Coze API 获取 {city_name} 的数据失败")
                return None
                
            # 合并数据
            destination_data = {
                'title': city_name,
                'description': coze_data.get('description', ''),
                'long_description': coze_data.get('long_description', ''),
                'location': city_name,
                'province': coze_data.get('province', ''),
                'country': coze_data.get('country', '中国'),
                'latitude': coze_data.get('latitude'),
                'longitude': coze_data.get('longitude'),
                'category': '城市',
                'best_season': coze_data.get('best_season', ''),
                'views_count': 0,
                'rating': 5.0
            }
            
            # 添加图片
            if mafengwo_data and mafengwo_data.get('cover_image'):
                destination_data['cover_image'] = mafengwo_data['cover_image']
                
            return destination_data
            
        except Exception as e:
            print(f"收集目的地数据时出错: {str(e)}")
            return None
            
    def _get_coze_data(self, city_name: str) -> Optional[Dict]:
        """从 Coze API 获取城市数据"""
        try:
            # 准备请求数据
            payload = {
                "workflow_id": self.workflow_id,
                "parameters": {
                    "city": city_name
                },
                "app_id": self.app_id
            }
            
            # 发送请求
            response = requests.post(
                self.coze_api_url,
                headers=self.coze_headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            # 打印原始响应内容
            print("Coze API 响应内容:")
            print(response.text)
            
            # 解析响应数据
            result_data = None
            for line in response.text.split('\n'):
                if not line.strip():
                    continue
                    
                # 解析 SSE 格式数据
                if not line.startswith('data: '):
                    continue
                    
                try:
                    # 提取 data 部分
                    data_str = line[6:]  # 跳过 'data: '
                    data = json.loads(data_str)
                    
                    if isinstance(data, dict) and 'content' in data:
                        # 先将 content 字符串解码为 bytes，再解码为 UTF-8 字符串
                        content_bytes = data['content'].encode('raw_unicode_escape')
                        content_str = content_bytes.decode('utf-8')
                        content = json.loads(content_str)
                        
                        if 'result' in content:
                            result_data = content['result']
                            # 打印解析过程
                            print("\n解析步骤:")
                            print("1. 原始 content:", data['content'])
                            print("2. 解码后的 content:", content_str)
                            print("3. 解析后的 content:", json.dumps(content, ensure_ascii=False))
                            print("4. 最终结果:", json.dumps(result_data, ensure_ascii=False))
                            break
                except json.JSONDecodeError as e:
                    print(f"JSON 解析错误: {str(e)}")
                    continue
                except Exception as e:
                    print(f"其他解析错误: {str(e)}")
                    continue
            
            if result_data:
                print("\n最终解析后的数据:")
                print(json.dumps(result_data, ensure_ascii=False, indent=2))
                    
            return result_data
            
        except Exception as e:
            print(f"从 Coze API 获取数据时出错: {str(e)}")
            return None 