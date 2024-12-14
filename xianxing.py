import requests
import json
import time
import hmac
import hashlib
import base64
from urllib.parse import quote

# 钉钉机器人的Webhook URL（不包含签名部分）和Secret
webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxxxxx" # 请替换为你的实际webhook_url
secret = 'SECxxxxxxxxxxxxxxxxxx'  # 请替换为你的实际Secret

# 天聚数行API配置
tianju_api_key = 'xxxxxxxxxxxxxxxxxx'  # 替换为你的天聚数行API Key
pyqwenan_api_url = 'https://apis.tianapi.com/pyqwenan/index'
moodpoetry_api_url = 'https://apis.tianapi.com/moodpoetry/index'


def generate_sign(secret, timestamp):
    string_to_sign = f'{timestamp}\n{secret}'
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    sign = quote(base64.b64encode(hmac_code))
    return sign


def get_message_from_api(api_url, params):
    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 200:
            return data.get('result', {})
        else:
            return {'content': 'API返回错误'}
    else:
        return {'content': 'API请求失败'}


def format_message(pyqwenan_result, moodpoetry_result):
    pyq_content = pyqwenan_result.get('content', '无法获取内容')
    pyq_source = pyqwenan_result.get('source', '未知来源')
    mood_title = moodpoetry_result.get('title', '无标题')
    mood_content = moodpoetry_result.get('content', '无法获取内容')
    mood_author = moodpoetry_result.get('author', '未知作者')

    message = (
        f"【每日一句】\n内容: {pyq_content}\n来源: {pyq_source}\n\n"
        f"【心情诗词】\n标题: {mood_title}\n内容: {mood_content}\n作者: {mood_author}"
    )
    return message


# 获取每日一句的消息内容
pyqwenan_params = {'key': tianju_api_key}
pyqwenan_result = get_message_from_api(pyqwenan_api_url, pyqwenan_params)

# 获取心情诗词的消息内容
moodpoetry_params = {'key': tianju_api_key, 'type': 2}  # 根据需要调整type参数
moodpoetry_result = get_message_from_api(moodpoetry_api_url, moodpoetry_params)

# 格式化消息内容
message_content = format_message(pyqwenan_result, moodpoetry_result)

# 创建签名
timestamp = str(round(time.time() * 1000))
sign = generate_sign(secret, timestamp)

# 完整的Webhook URL
complete_webhook_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"

# 构建推送的消息内容
message = {
    "msgtype": "text",
    "text": {
        "content": message_content
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
