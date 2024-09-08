from datetime import date, datetime, timedelta
import math
from wechatpy import WeChatClient, WeChatClientException
from wechatpy.client.api import WeChatMessage
import requests
import os
import random

word_list =[ "今天流的汗，都是明天减的脂。",
"不为减肥找借口，只为健康找方法。",
"每一滴汗水，都是在雕刻更好的自己。",
"管住嘴，迈开腿，离梦想的身材更近一步。",
"坚持是一种信仰，瘦下来是一种信念。",
"少吃一口，收获更多自信。",
"现在不努力减肥，将来就要努力看医生。",
"汗水是燃烧脂肪的证据。",
"美好的身材始于自律。",
"每一次放弃高热量食物，都是离目标更近一步。",
            "只要你勇敢追求，梦想就会成真。",

]

with open('word_list_file.txt', 'r') as f:
  word_list += f.readlines()
print('word_list size:', len(word_list))
nowtime = datetime.utcnow() + timedelta(hours=8)  # 东八区时间
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d") #今天的日期

start_date = os.getenv('START_DATE')
city = os.getenv('CITY')
birthday = os.getenv('BIRTHDAY')

app_id = os.getenv('APP_ID')
app_secret = os.getenv('APP_SECRET')

user_ids = os.getenv('USER_ID', '').split("\n")
template_id = os.getenv('TEMPLATE_ID')

if app_id is None or app_secret is None:
  print('请设置 APP_ID 和 APP_SECRET')
  exit(422)

if not user_ids:
  print('请设置 USER_ID，若存在多个 ID 用回车分开')
  exit(422)

if template_id is None:
  print('请设置 TEMPLATE_ID')
  exit(422)

# weather 直接返回对象，在使用的地方用字段进行调用。
def get_weather():
  # if city is None:
  #   print('请设置城市')
  #   return None
  # url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
  # res = requests.get(url).json()
  # if res is None:
  #   return None
  # weather = res['data']['list'][0]
  return {"defaultkey":"未获取"}

# 获取当前日期为星期几
def get_week_day():
  week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
  week_day = week_list[datetime.date(today).weekday()]
  return week_day

# 纪念日正数
def get_memorial_days_count():
  if start_date is None:
    print('没有设置 START_DATE')
    return 0
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

# 生日倒计时
def get_birthday_left():
  if birthday is None:
    print('没有设置 BIRTHDAY')
    return 0
  next = datetime.strptime(str(today.year) + "-" + birthday, "%Y-%m-%d")
  if next < nowtime:
    next = next.replace(year=next.year + 1)
  return (next - today).days

# 彩虹屁 接口不稳定，所以失败的话会重新调用，直到成功
def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def format_temperature(temperature):
  return math.floor(temperature)

# 随机颜色
def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)

try:
  client = WeChatClient(app_id, app_secret)
except WeChatClientException as e:
  print('微信获取 token 失败，请检查 APP_ID 和 APP_SECRET，或当日调用量是否已达到微信限制。')
  exit(502)

wm = WeChatMessage(client)
weather = get_weather()
if weather is None:
  print('获取天气失败')
  exit(422)
data = {
  "city": {
    "value": city,
    "color": get_random_color()
  },
  "date": {
    "value": today.strftime('%Y年%m月%d日'),
    "color": get_random_color()
  },
  "week_day": {
    "value": get_week_day(),
    "color": get_random_color()
  },
  "weather": {
    # "value": weather['weather'],
    # "value": "未知天气",
    "value": str(len(word_list)) + " " + random.choice(word_list),
    "color": get_random_color()
  },
  "humidity": {
    "value": "default", # weather['humidity'],
    "color": get_random_color()
  },
  "wind": {
    "value":"default", #  weather['wind'],
    "color": get_random_color()
  },
  "air_data": {
    "value": "default", # weather['airData'],
    "color": get_random_color()
  },
  "air_quality": {
    "value": "default", # weather['airQuality'],
    "color": get_random_color()
  },
  "temperature": {
    "value": "default", # math.floor(weather['temp']),
    "color": get_random_color()
  },
  "highest": {
    "value": "default", # math.floor(weather['high']),
    "color": get_random_color()
  },
  "lowest": {
    "value": "default", # math.floor(weather['low']),
    "color": get_random_color()
  },
  "love_days": {
    "value": get_memorial_days_count(),
    "color": get_random_color()
  },
  "birthday_left": {
    "value": get_birthday_left(),
    "color": get_random_color()
  },
  "words": {
    "value": get_words(),
    "color": get_random_color()
  },
}

if __name__ == '__main__':
  count = 0
  try:
    for user_id in user_ids:
      res = wm.send_template(user_id, template_id, data)
      count+=1
  except WeChatClientException as e:
    print('微信端返回错误：%s。错误代码：%d' % (e.errmsg, e.errcode))
    exit(502)

  print("发送了" + str(count) + "条消息")
