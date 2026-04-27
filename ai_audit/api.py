import requests
import json
from django.conf import settings


class GPT5API:
    """
    GPT-5 API 调用类
    """
    def __init__(self):
        # API 配置 - 请在 settings.py 中设置
        self.api_url = getattr(settings, 'GPT5_API_URL', 'https://api.example.com/gpt5')
        self.api_token = getattr(settings, 'GPT5_API_TOKEN', 'YOUR_API_TOKEN_HERE')
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def generate_test_logic(self, data):
        """
        生成测试逻辑
        """
        payload = {
            'prompt': f"基于以下数据生成信贷审计测试逻辑:\n{json.dumps(data, ensure_ascii=False)}",
            'max_tokens': 1000,
            'temperature': 0.7
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API调用错误: {e}")
            return None
    
    def update_test_logic(self, test_logic, feedback):
        """
        根据反馈更新测试逻辑
        """
        payload = {
            'prompt': f"基于以下反馈更新测试逻辑:\n测试逻辑: {test_logic}\n反馈: {feedback}",
            'max_tokens': 1000,
            'temperature': 0.7
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API调用错误: {e}")
            return None


def get_api_instance():
    """
    获取API实例
    """
    return GPT5API()
