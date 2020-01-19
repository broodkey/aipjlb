#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# 引用Web Server套件
from flask import Flask, request, abort

# 從linebot 套件包裡引用 LineBotApi 與 WebhookHandler 類別
from linebot import (
    LineBotApi, WebhookHandler
)

# 引用無效簽章錯誤
from linebot.exceptions import (
    InvalidSignatureError
)

# 載入json處理套件
import json


# In[ ]:


# 載入基礎設定檔
secretFileContentJson=json.load(open("line_secret_key",'r',encoding="utf-8"))
server_url=secretFileContentJson.get("server_url")

# 設定Server啟用細節
app = Flask(__name__,static_url_path = "/images" , static_folder = "/images/")

# 生成實體物件
line_bot_api = LineBotApi(secretFileContentJson.get("channel_access_token"))
handler = WebhookHandler(secretFileContentJson.get("secret_key"))

# 啟動server對外接口，使Line能丟消息進來
@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# In[ ]:


# 將消息模型，文字收取消息與文字寄發消息 引入
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

# 消息清單
reply_message_list = [
    TextSendMessage(text="歡迎加入好友"),
]

# 載入Follow事件
from linebot.models.events import (
    FollowEvent
)

# 告知handler，如果收到FollowEvent，則做下面的方法處理
# handler如果收到關注事件時，執行下面的方法
@handler.add(FollowEvent)
def reply_text_and_get_user_profile(event):
    # 取出消息內User的資料
    user_profile = line_bot_api.get_profile(event.source.user_id)

    # 將用戶資訊存在檔案內
    with open("users.txt", "a") as myfile:
        myfile.write(json.dumps(vars(user_profile), sort_keys=True))
        myfile.write('\r\n')

    # 將菜單綁定在用戶身上
    linkRichMenuId = secretFileContentJson.get("rich_menu_id")
    linkResult = line_bot_api.link_rich_menu_to_user(secretFileContentJson["self_user_id"], linkRichMenuId)

    # 回覆文字消息與圖片消息
    line_bot_api.reply_message(
        event.reply_token,
        reply_message_list
    )


# In[ ]:


'''

若收到圖片消息時，

先回覆用戶文字消息，並從Line上將照片拿回。

'''
# 將消息模型，文字收取消息與文字寄發消息 引入
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageMessage
)

import csv

@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Image has Upload'+ ' ' + event.message.id))
    
    user_id_exist = 0
    dict_to_file = {}
    for d in collect_report:
        if d['user_id'] == event.source.user_id:
            d['image_name'] = event.message.id+'.jpg'
            user_id_exist = 1
            dict_to_file = d
            break
    if user_id_exist == 0:
        return 'OK'
    
    message_content = line_bot_api.get_message_content(event.message.id)
    with open('images/'+event.message.id+'.jpg', 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
            
    # 將資訊存在檔案內
    if len(dict_to_file) == 7:
        with open('user_report.csv', "a", encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow([dict_to_file['display_name'],
                                 dict_to_file['user_id'],
                                 dict_to_file['address'],
                                 dict_to_file['latitude'],
                                 dict_to_file['longitude'],
                                 dict_to_file['image_name']
                                ])
        collect_report.remove(dict_to_file)
        print(collect_report)


# In[ ]:


# 將消息模型，文字收取消息與文字寄發消息 引入
from linebot.models import (
    MessageEvent, LocationMessage
)

import csv

# 用戶點擊傳送位置，觸發LocationMessage，對其回傳做相對應處理
@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    # 取出消息內User的資料
    user_profile = line_bot_api.get_profile(event.source.user_id)
    display_name = vars(user_profile)["display_name"]
    user_id = vars(user_profile)["user_id"]
    address = event.message.address
    latitude = event.message.latitude
    longitude = event.message.longitude

    user_id_exist = 0
    dict_to_file = {}
    for d in collect_report:
        if d['user_id'] == event.source.user_id:
            d['display_name'] = display_name
            d['address'] = address
            d['latitude'] = latitude
            d['longitude'] = longitude
            user_id_exist = 1
            dict_to_file = d
            break
    if user_id_exist == 0:
        return 'OK'

    # 將資訊存在檔案內
    if len(dict_to_file) == 7:
        with open('user_report.csv', "a", encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow([dict_to_file['display_name'],
                                 dict_to_file['user_id'],
                                 dict_to_file['address'],
                                 dict_to_file['latitude'],
                                 dict_to_file['longitude'],
                                 dict_to_file['image_name']
                                ])
        collect_report.remove(dict_to_file)
        print(collect_report)


# In[ ]:


#引入所需要的消息與模板消息
from linebot.models import (
    MessageEvent, TemplateSendMessage , PostbackEvent
)

#引入按鍵模板
from linebot.models.template import(
    ButtonsTemplate
)

ButtonsTemplateJsonString = """
{
  "type": "template",
  "altText": "this is a buttons template",
  "template": {
    "type": "buttons",
    "actions": [
      {
        "type": "uri",
        "label": "上傳照片",
        "uri": "line://nv/cameraRoll/single"
      },
      {
        "type": "uri",
        "label": "回報位置",
        "uri": "line://nv/location"
      }
    ],
    "title": "道路坑洞回報",
    "text": "照片及位置"
  }
}
"""
ButtonsTemplate = TemplateSendMessage.new_from_json_dict(json.loads(ButtonsTemplateJsonString))


# In[ ]:


@handler.add(PostbackEvent)
def handle_post_message(event):
    user_profile = line_bot_api.get_profile(event.source.user_id)
    
    user_id_exist = 0
    if (event.postback.data.find('資料 1') == 0):
        for d in collect_report:
            if d['user_id'] == event.source.user_id:
                d['token'] = event.reply_token
                user_id_exist = 1
                break
        if user_id_exist == 0:
            collect_report.append({'user_id':event.source.user_id, 'token':event.reply_token})
            
        print(collect_report)
        line_bot_api.reply_message(
            event.reply_token,
            ButtonsTemplate)


# In[ ]:


# 產生user_report.csv 紀錄使用者回報照片以及位置
import os
import csv
# 若user_report.csv不存在則新增檔案並寫好欄位名稱
if os.path.exists('user_report.csv') == False:
    with open('user_report.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(['display_name', 'user_id', 
                             'address', 'latitude', 'longitude', 
                             'image_name'])
collect_report = []


# In[ ]:


#  '''

#  執行此句，啟動Server，觀察後，按左上方塊，停用Server

#  '''

# if __name__ == "__main__":
#     app.run(host='0.0.0.0')


# In[ ]:


#  '''

#  Application 運行（heroku版）

#  '''

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])




