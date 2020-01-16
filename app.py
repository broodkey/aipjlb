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

# 將消息模型，文字收取消息與文字寄發消息 引入
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

# 消息清單
reply_message_list = [
    TextSendMessage(text="test1"),
    TextSendMessage(text="test2"),
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

#  '''

#  執行此句，啟動Server，觀察後，按左上方塊，停用Server

#  '''

 # if __name__ == "__main__":
 #     app.run(host='0.0.0.0')

#  '''

#  Application 運行（heroku版）

#  '''

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])