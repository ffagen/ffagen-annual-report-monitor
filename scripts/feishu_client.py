"""
年报公告监控 - 飞书客户端
发送富文本消息到飞书群
"""
import requests
import json
import time
from typing import Optional
from config import FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_CHAT_ID, HEADERS

# 飞书API地址
FEISHU_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
FEISHU_MESSAGE_URL = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"

class FeishuClient:
    """飞书客户端"""
    
    def __init__(self):
        self.app_id = FEISHU_APP_ID
        self.app_secret = FEISHU_APP_SECRET
        self.chat_id = FEISHU_CHAT_ID
        self._token = None
        self._token_expires_at = 0
    
    def _get_token(self) -> Optional[str]:
        """获取tenant_access_token"""
        # 如果token还在有效期内，直接返回
        if self._token and time.time() < self._token_expires_at - 60:
            return self._token
        
        try:
            response = requests.post(
                FEISHU_TOKEN_URL,
                headers={"Content-Type": "application/json"},
                json={"app_id": self.app_id, "app_secret": self.app_secret},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") == 0:
                self._token = data.get("tenant_access_token")
                # token有效期是2小时，记录过期时间
                self._token_expires_at = time.time() + 7200
                print(f"[飞书] 获取token成功")
                return self._token
            else:
                print(f"[飞书] 获取token失败: {data.get('msg')}")
                return None
        except Exception as e:
            print(f"[飞书] 获取token异常: {e}")
            return None
    
    def send_text_message(self, content: str) -> bool:
        """发送纯文本消息"""
        return self.send_message({"msg_type": "text", "content": {"text": content}})
    
    def send_rich_text_message(self, title: str, content: str) -> bool:
        """发送富文本消息（post类型）"""
        post_content = {
            "zh_cn": {
                "title": title,
                "content": [
                    [{"tag": "text", "text": content}]
                ]
            }
        }
        return self.send_message({"msg_type": "post", "content": {"post": post_content}})
    
    def send_interactive_message(self, card: dict) -> bool:
        """发送卡片消息"""
        token = self._get_token()
        if not token:
            print("[飞书] 未获取到token，无法发送消息")
            return False
        
        try:
            response = requests.post(
                FEISHU_MESSAGE_URL,
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                json=card,
                timeout=15
            )
            result = response.json()
            
            if result.get("code") == 0:
                print(f"[飞书] 消息发送成功，message_id: {result.get('data', {}).get('message_id')}")
                return True
            else:
                print(f"[飞书] 消息发送失败: {result.get('msg')}")
                return False
        except Exception as e:
            print(f"[飞书] 发送消息异常: {e}")
            return False
    
    def send_message(self, message: dict) -> bool:
        """发送消息（通用方法）"""
        token = self._get_token()
        if not token:
            print("[飞书] 未获取到token，无法发送消息")
            return False
        
        try:
            payload = {
                "receive_id": self.chat_id,
                "msg_type": message.get("msg_type", "text"),
                "content": json.dumps(message.get("content", {}))
            }
            
            response = requests.post(
                FEISHU_MESSAGE_URL,
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                json=payload,
                timeout=15
            )
            result = response.json()
            
            if result.get("code") == 0:
                print(f"[飞书] 消息发送成功")
                return True
            else:
                print(f"[飞书] 消息发送失败: {result.get('msg')}")
                return False
        except Exception as e:
            print(f"[飞书] 发送消息异常: {e}")
            return False
    
    def send_html_card(self, title: str, html_content: str) -> bool:
        """发送HTML格式的卡片消息"""
        card = {
            "receive_id": self.chat_id,
            "msg_type": "interactive",
            "content": json.dumps({
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {"tag": "plain_text", "text": title},
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": html_content
                        }
                    }
                ]
            })
        }
        return self.send_message(card)


def test_feishu_client():
    """测试飞书客户端"""
    from config import is_configured
    
    if not is_configured():
        print("[测试] 飞书配置不完整，跳过发送测试")
        return False
    
    client = FeishuClient()
    return client.send_text_message("🧪 [测试] 年报监控系统连接测试成功！")


if __name__ == "__main__":
    test_feishu_client()
