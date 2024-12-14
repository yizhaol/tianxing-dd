import requests
import json
import time
import hmac
import hashlib
import base64
from urllib.parse import quote

# 钉钉机器人的Webhook URL（不包含签名部分）和Secret
webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxxxxxxx"
secret = 'SECxxxxxxxxxxxxxxxxxxxx'  # 请替换为你的实际Secret
# 天聚数行API配置、
tianju_api_url = 'https://apis.tianapi.com/moodpoetry/index'  #在天聚数行申请接口
tianju_api_key = 'xxxxxxxxxxxxxxxxxxxx'  # 替换为你的天聚数行API Key


def generate_sign(secret, timestamp):
    string_to_sign = f'{timestamp}\n{secret}'
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    sign = quote(base64.b64encode(hmac_code))
    return sign


def get_message_from_tianju(api_key):
    params = {
        'key': api_key  # 天聚数行API需要的参数，#部分接口需要多个参数在这添加即可，并同步调整46行代码例如：'type': poetry_type
    }

    response = requests.get(tianju_api_url, params=params)

    if response.status_code == 200:
        data = response.json()
        result = data.get('result', {})
        content = result.get('content', '无法获取内容')
        source = result.get('source', '未知来源')
        return content, source
    else:
        return 'API请求失败', '未知来源'


# 获取消息内容
content, source = get_message_from_tianju(tianju_api_key) #部分接口需要多个参数，与30行代码同步调整例如：get_message_from_tianju(tianju_api_key,2)

# 创建签名
timestamp = str(round(time.time() * 1000))
sign = generate_sign(secret, timestamp)

# 完整的Webhook URL
complete_webhook_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"

# 构建推送的消息内容
message = {
    "msgtype": "text",
    "text": {
        "content": f" {content}"   #如果需要来源请改为"content": f" {content}\n来源: {source}"
    }
}

response = requests.post(
    complete_webhook_url,
    headers={"Content-Type": "application/json"},
    data=json.dumps(message)
)

# 检查响应状态码
if response.status_code == 200:
    print("消息发送成功")
else:
    print("消息发送失败")


