Tài liệu hướng dẫn dành cho nhà phát triển muốn xây dựng và tích hợp chatbot vào hệ sinh thái Zalo thông qua nền tảng Zalo Bot Platform.

Zalo Bot là một tài khoản tự động (bot) hoạt động trên nền tảng Zalo, cho phép doanh nghiệp hoặc nhà phát triển tương tác tự động với người dùng thông qua tin nhắn ngay trong cửa sổ chat.
Zalo Bot hỗ trợ triển khai các giải pháp tự động hóa (automation) trên nền tảng Zalo. Giúp doanh nghiệp dễ dàng xây dựng quy trình gửi thông báo, kết nối với các hệ thống nội bộ như ERP, CRM, CDP... Từ đó giúp chuẩn hóa quy trình, tăng tốc vận hành và tối ưu chi phí.

Để tạo Zalo Bot, vui lòng thực hiện theo hướng dẫn sau:

Bước 1: Truy cập Zalo OA
Mở ứng dụng Zalo
Tìm kiếm OA Zalo Bot Manager
Chọn Tạo bot trong menu cửa sổ chat để truy cập ứng dụng Zalo Bot Creator
Bước 2: Thiết lập thông tin Bot
Nhập tên Bot (bắt buộc bắt đầu bằng tiền tố Bot, ví dụ: Bot MyShop) và các thông tin cần thiết.
Nhấn Tạo Bot để xác nhận
Sau khi tạo thành công, hệ thống sẽ gửi:
Thông tin Bot
Bot Token qua tin nhắn cho tài khoản Zalo của bạn.
Bước 3: Lập trình Bot
Sử dụng Node.js, Python hoặc nền tảng không cần code (No-code) để tùy biến theo nhu cầu của bạn.
Zalo Bot hỗ trợ 2 cơ chế giao tiếp để cập nhật thông tin:
Long polling: gửi yêu cầu định kỳ để lấy tin nhắn mới. Để bắt đầu chạy thử và phát triển Bot, hãy sử dụng API getUpdates ở máy local, sau đó nhắn tin đến Bot của bạn. Bạn sẽ nhận được tin nhắn và có thể sendMessage ngược lại cho người dùng.
Webhook: hệ thống Zalo sẽ gửi tin nhắn đến Webhook URL bạn đã thiết lập, tham khảo API setWebhook.

Zalo sử dụng mô hình Bot Token xác thực và cho phép bot sử dụng API.

Bot Token
Được cung cấp sau khi tạo bot thành công, Token này sẽ không hết hạn cho tới khi bạn chủ động reset. Token sẽ có dạng 12345689:abc-xyz và được dùng để gọi tất cả các API với phương thức như sau:

 https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/functionName

mẹo
Để cài đặt lại Bot Token, vui lòng truy cập Zalo Bot Creator, chọn thiết lập và làm theo hướng dẫn. Khi thay đổi thành công, hệ thống sẽ gửi Token mới cho bạn qua tin nhắn Zalo.

Để gửi yêu cầu đến hệ thống Open APIs của Zalo Bot, bạn sử dụng Bot Token đã được cấp và làm theo hướng dẫn bên dưới.

Định dạng URL
Tất cả các truy vấn đến Zalo Bot API phải được thực hiện qua giao thức HTTPS và có định dạng như sau:

https://bot-api.zaloplatforms.com/bot<BOT_TOKEN>/<functionName>

Ví dụ:

https://bot-api.zaloplatforms.com/bot123456789:abc123xyz/getMe

Phương thức HTTP hỗ trợ
GET
POST
Cách truyền tham số
Zalo Bot hỗ trợ cả 2 phương thức HTTP GET và POST cho tất cả các API, với các cách để truyền tham số như sau:

Chuỗi truy vấn URL (query string)
Ví dụ: ...?chat_id=123456&text=Hello

application/x-www-form-urlencoded
Dạng form tiêu chuẩn (dùng với POST đơn giản)

application/json
Gửi payload dạng JSON-object

multipart/form-data
Dùng khi cần tải lên file như ảnh, tài liệu,...

Tuy nhiên, bạn nên cân nhắc sử dụng phương thức HTTP GET cho các API dùng để truy xuất dữ liệu và POST cho các API dùng để thay đổi (ghi/cập nhật) thông tin dữ liệu.

Phản hồi từ API
Phản hồi từ Zalo Bot API luôn là dạng JSON-object, gồm các trường thông tin chính sau:

Trường	Ý nghĩa
ok	true nếu thành công, false nếu có lỗi
result	Dữ liệu trả về nếu thành công
description	Mô tả lỗi ngắn gọn (nếu có)
error_code	Mã lỗi hệ thống
Lưu ý
Tất cả truy vấn gửi đến Zalo Bot API phải sử dụng encoding UTF-8.
Các tên API (method name) có phân biệt chữ hoa và chữ thường.

#getme

Sử dụng phương thức này để kiểm tra Bot Token, nếu token hợp lệ sẽ trả về các thông tin cơ bản về Bot của bạn.

URL: https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/getMe
Method: POST
Response Type: application/json
Sample code
Nodejs
cURL
const axios = require("axios");

const entrypoint = `https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/getMe`;
const response = await axios.post(entrypoint, {});

Parameters
Không yêu cầu tham số đi kèm.

Sample response
{
  "ok": true,
  "result": {
    "id": "1459232241454765289",
    "account_name": "bot.VDKyGxQvc",
    "account_type": "BASIC",
    "can_join_groups": false
  }
}

#getupdates
Hệ thống Zalo hỗ trợ 2 cách độc lập và loại trừ lẫn nhau để bot của bạn nhận được các tin nhắn mới:

Sử dụng phương thức getUpdates, dựa trên cơ chế long polling.
Sử dụng Webhook.
Lưu ý
Phương thức getUpdates sẽ không hoạt động nếu bạn đã thiết lập Webhook trước đó (khi đó, vui lòng sử dụng phương thức deleteWebhook để xóa cấu hình Webhook trước khi sử dụng API này). Chỉ nên sử dụng API này để chạy local, trong môi trường development, thử nghiệm, với môi trường production, bạn nên thiết lập Webhook để tránh bỏ lỡ event.

URL: https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/getUpdates
Method: POST
Response Type: application/json
Sample code
Nodejs
cURL
const axios = require("axios");

const entrypoint = `https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/getUpdates`;
const response = await axios.post(entrypoint, {
  timeout: 30
});

Parameters
Trường	Kiểu dữ liệu	Bắt buộc	Mô tả
timeout	String	false	Thời gian timeout của HTTP Request tính theo giây. Mặc định hệ thống sẽ lấy thời gian timeout là 30 giây.
Sample response
Dữ liệu tin nhắn nhận được sẽ là dạng JSON object, tham khảo dữ liệu mẫu tương tự tại Webhook.

mẹo
Xem hướng dẫn xây dựng Chatbot cơ bản với cơ chế getUpdates tại đây.

#setwebhook

API cho phép cấu hình Webhook URL cho Bot của bạn.

URL: https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/setWebhook
Method: POST
Response Type: application/json
Sample code
Nodejs
cURL
const axios = require("axios");

const entrypoint = `https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/setWebhook`;
const response = await axios.post(entrypoint, {
  url: "https://your-webhookurl.com",
  secret_token: "mykey-abcyxz"
});


Parameters
Trường	Kiểu dữ liệu	Bắt buộc	Mô tả
url	String	true	URL nhận thông báo dạng HTTPS.
secret_token	String	true	Một khóa bí mật từ 8 tới 256 ký tự, để xác thực yêu cầu từ Zalo gọi về hệ thống của bạn. Token sẽ được đính kèm trong header "X-Bot-Api-Secret-Token" trong tất cả các yêu cầu từ Zalo gọi tới hệ thống của bạn.
Sample response
{
  "ok": true,
  "result": {
    "url": "https://your-webhookurl.com",
    "updated_at": 1749538250568
  }
}

#deletewebhook

Sử dụng phương thức này để gỡ bỏ thiết lập webhook nếu bạn quyết định chuyển lại sang getUpdates. Phương thức này sẽ trả về True khi xử lý thành công.

URL: https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/deleteWebhook
Method: POST
Response Type: application/json
Sample code
Nodejs
cURL
const axios = require("axios");

const entrypoint = `https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/deleteWebhook`;
const response = await axios.post(entrypoint, {});

Parameters
Không yêu cầu tham số đi kèm.

Sample response
{
  "ok": true,
  "result": {
    "url": "",
    "updated_at": 1749538250568
  }
}

#getWebhookInfo

API cho phép lấy trạng thái cấu hình hiện tại của webhook

URL: https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/getWebhookInfo
Method: POST
Response Type: application/json
Sample code
Nodejs
cURL
const axios = require("axios");

const entrypoint = `https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/getWebhookInfo`;
const response = await axios.post(entrypoint, {});

Parameters
Không yêu cầu tham số đi kèm.

Sample response
{
  "ok": true,
  "result": {
    "url": "https://your-webhookurl.com",
    "updated_at": 1749633372026
  }
}

#sendMessage

API cho phép Bot của bạn gửi tin nhắn văn bản đến người dùng hoặc các cuộc trò chuyện.

URL: https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/sendMessage
Method: POST
Response Type: application/json
Sample code
Nodejs
cURL
const axios = require("axios");

const entrypoint = `https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/sendMessage`;
const response = await axios.post(entrypoint, {
  chat_id: "abc.xyz",
  text: "Hello"
});

Parameters
Trường	Kiểu dữ liệu	Bắt buộc	Mô tả
chat_id	String	true	ID của người nhận hoặc cuộc trò chuyện
text	String	true	Nội dung văn bản của tin nhắn sẽ được gửi, với độ dài từ 1 đến 2000 ký tự
Sample response
{
  "ok": true,
  "result": {
    "message_id": "82599fa32f56d00e8941",
    "date": 1749632637199
  }
}

#sendPhoto

API cho phép Bot của bạn gửi tin nhắn hình ảnh đến người dùng hoặc các cuộc trò chuyện.

URL: https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/sendPhoto
Method: POST
Response Type: application/json
Sample code
Nodejs
cURL
const axios = require("axios");

const entrypoint = `https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/sendPhoto`;
const response = await axios.post(entrypoint, {
  chat_id: "abc.xyz",
  caption: "My photo",
  photo: "https://placehold.co/600x400"
});


Parameters
Trường	Kiểu dữ liệu	Bắt buộc	Mô tả
chat_id	String	true	ID của người nhận hoặc cuộc trò chuyện
photo	String	true	Đường dẫn hình ảnh sẽ được gửi
caption	String	false	Nội dung văn bản của tin nhắn sẽ được gửi kèm, với độ dài từ 1 đến 2000 ký tự
Sample response
{
  "ok": true,
  "result": {
    "message_id": "82599fa32f56d00e8941",
    "date": 1749632637199
  }
}

#sendSticker

API cho phép Bot của bạn gửi tin nhắn Sticker đến người dùng hoặc các cuộc trò chuyện.

URL: https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/sendSticker
Method: POST
Response Type: application/json
Sample code
Nodejs
cURL
const axios = require("axios");

const entrypoint = `https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/sendSticker`;
const response = await axios.post(entrypoint, {
  chat_id: "abc.xyz",
  sticker: "0e078a2fb66a5f34067b"
});


Parameters
Trường	Kiểu dữ liệu	Bắt buộc	Mô tả
chat_id	String	true	ID của người nhận hoặc cuộc trò chuyện
sticker	String	true	Truyền vào stricker lấy từ nguồn: https://stickers.zaloapp.com/. Vui lòng xem video hướng dẫn tại đây: https://vimeo.com/649330161
Sample response
{
  "ok": true,
  "result": {
    "message_id": "82599fa32f56d00e8941",
    "date": 1749632637199
  }
}

#sendChatAction

API cho phép Bot hiển thị một trạng thái tạm thời trong cuộc trò chuyện, chẳng hạn như đang soạn tin nhắn hoặc đang gửi ảnh.

URL: https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/sendChatAction
Method: POST
Response Type: application/json
Sample code
Nodejs
cURL
const axios = require("axios");

const entrypoint = `https://bot-api.zaloplatforms.com/bot${BOT_TOKEN}/sendChatAction`;
const response = await axios.post(entrypoint, {
  chat_id: "abc.xyz",
  action: "typing"
});

Parameters
Trường	Kiểu dữ liệu	Bắt buộc	Mô tả
chat_id	String	true	ID của người nhận hoặc cuộc trò chuyện
action	String	true	Loại hành động mà bot sẽ phát đi. Các loại hành động có sẵn bao gồm:
typing: Cho tin nhắn văn bản.
upload_photo: Cho ảnh (Sắp ra mắt).
Sample response
{
  "ok": true
}

#Webhook

Zalo sẽ gửi các HTTP Request (phương thức POST) đến Webhook URL bạn đã thiết lập khi có tương tác từ người dùng hoặc các thay đổi liên quan tới Bot.

Tất cả các request sẽ được gửi kèm headers X-Bot-Api-Secret-Token với giá trị là secret_token bạn đã thiết lập trước đó, vui lòng xác thực lại token này trước khi xử lý để đảm bảo yêu cầu hợp lệ.

URL: https://your-webhookurl.com
Method: POST
Headers: X-Bot-Api-Secret-Token
Request Type: application/json
mẹo
Nên thiết lập Webhook URL với domain sử dụng HTTPS để tăng tính bảo mật cho hệ thống của bạn. Xem hướng dẫn thiết lập tại setWebhook.

Sample code
src/backend.ts
    app.use(express.json());
    const WEBHOOK_SECRET_TOKEN = 'your-secret-token';

+   .post("/webhooks", async (req, res) => {
+     const secretToken = req.headers["x-bot-api-secret-token"];    
+     if (secretToken !== WEBHOOK_SECRET_TOKEN) {
+       return res.status(403).json({ message: "Unauthorized" });
+     } 
+     let body = req.body;
+     // Handle your logic at here
+     res.json({ message: "Success" });
+   })
    .listen(port, () => {
      console.log(`Server running at http://localhost:${port}`);
    });

Parameters
Dữ liệu được gửi từ Zalo Server sẽ là dạng JSON object, gồm các trường thông tin chính sau:

Trường	Ý nghĩa
ok	Luôn có giá trị true
result	Dữ liệu thông tin cho sự kiện, với từng loại sự kiện có được gửi kèm các trường thông tin tương ứng.
Result
Trường	Kiểu dữ liệu	Bắt buộc	Mô tả
event_name	String	true	Tên sự kiện, sẽ nhận một trong các giá trị sau:
message.text.received: nhận được một tin nhắn văn bản.
message.image.received: nhận được một tin nhắn dạng hình ảnh.
message.sticker.received: nhận được một tin nhắn Sticker.
message.unsupported.received: nhận được một tin nhắn chưa hỗ trợ xử lý.
message	String	false	Nếu là sự kiện có tin nhắn mới, bạn sẽ nhận được thông tin chi tiết về message. Tùy theo từng loại tin nhắn sẽ có thêm các trường thông tin tương ứng. Tham khảo bảng đặc tả bên dưới
Sample response
{
  "ok": true,
  "result": {
    "message": {
      "from": {
        "id": "6ede9afa66b88fe6d6a9",
        "display_name": "Ted",
        "is_bot": false
      },
      "chat": {
        "id": "6ede9afa66b88fe6d6a9",
        "chat_type": "PRIVATE"
      },
      "text": "Xin chào",
      "message_id": "2d758cb5e222177a4e35",
      "date": 1750316131602
    },
    "event_name": "message.text.received"
  }
}

Message
Trường	Kiểu dữ liệu	Bắt buộc	Mô tả
from	JSON object	true	Thông tin người gửi tin nhắn
chat	JSON object	true	Thông tin cuộc trò chuyện. Trong đó chat_type sẽ là một trong các giá trị:
PRIVATE: cuộc hội thoại cá nhân.
GROUP: cuộc hội thoại với nhóm (Sắp ra mắt).
Sử dụng chat.id để gửi tin nhắn phản hồi tới cuộc trò chuyện.
text	String	false	Nội dung của tin nhắn văn bản
photo	String	false	Đường dẫn hình ảnh của tin nhắn hình ảnh
caption	String	false	Nội dung văn bản được gửi kèm tin nhắn hình ảnh
sticker	String	false	Truyền vào stricker lấy từ nguồn: https://stickers.zaloapp.com/. Vui lòng xem video hướng dẫn tại đây: https://vimeo.com/649330161
url	String	false	Đường dẫn của sticker
cảnh báo
Trường hợp tài khoản người gửi tin nhắn thuộc nhóm đối tượng đặc biệt (bao gồm nhưng không giới hạn: trẻ em, người khuyết tật, người không biết chữ,...), thay vì nhận nội dung tin nhắn, hệ thống của bạn sẽ nhận được sự kiện webhook message.unsupported.received, nhằm đảm bảo việc xử lý dữ liệu tuân thủ quy định pháp luật hiện hành.

#Best practices

##1. Hướng dẫn xây dựng Zalo Bot đơn giản với cơ chế Polling
Dưới đây là hướng dẫn xây dựng Zalo Bot cơ bản sử dụng chế độ Polling, phù hợp cho người mới bắt đầu và có thể dễ dàng chạy trên máy local.

Bước 1: Hiểu sơ lược về Zalo Bot
Zalo Bot là một tài khoản tự động (bot) hoạt động trên nền tảng Zalo, cho phép tương tác với người dùng thông qua tin nhắn. Bot có thể giúp bạn:

Trả lời tin nhắn theo từ khóa, yêu cầu...
Gửi thông tin cảnh báo
Tự động phản hồi đơn hàng, hỗ trợ khách hàng, khảo sát, v.v.
Bước 2: Tạo Bot
Để tạo Zalo Bot, vui lòng làm theo hướng dẫn tại đây. Sau khi tạo Bot, bạn sẽ nhận được thông tin Bot Token để tiến hành tích hợp API.

Bước 3: Lập trình Bot
Tham khảo code mẫu bên dưới để lập trình Bot đơn giản sử dụng cơ chế getUpdates và Zalo Bot SDK, phù hợp với môi trường Development, nhu cầu chạy thử nghiệm từ local trong quá trình tích hợp.

Python: Tham khảo thêm tài liệu tại python-zalo-bot.
Nodejs: Tham khảo thêm tài liệu tại node-zalo-bot.
Python
Nodejs

from zalo_bot import Update
from zalo_bot.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Hàm xử lý cho lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Chào {update.effective_user.display_name}! Tôi là chatbot!")

# Hàm xử lý cho lệnh /echo
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = " ".join(context.args)
    if message:
        await update.message.reply_text(f"Bạn vừa nói: {message}")
    else:
        await update.message.reply_text("Hãy nhập gì đó sau lệnh /echo")

if __name__ == "__main__":
    app = ApplicationBuilder().token("YOUR TOKEN HERE").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("echo", echo))

    print("🤖 Bot đang chạy...")
    app.run_polling()

##2. Hướng dẫn xây dựng Zalo Bot với cơ chế Webhook
Dưới đây là hướng dẫn xây dựng Zalo Bot sử dụng cơ chế Webhook dành cho người mới bắt đầu:

Mục tiêu
Tạo một bot Zalo sử dụng cơ chế Webhook để nhận sự kiện từ người dùng.
Xử lý các sự kiện như nhận tin nhắn, gửi phản hồi, gửi ảnh,...
Hiện thực bằng NodeJS hoặc Python sử dụng các SDK có sẵn.
Bước 1: Tạo Bot
Để tạo Zalo Bot, vui lòng làm theo hướng dẫn tại đây. Sau khi tạo Bot, bạn sẽ có thông tin Bot Token để tích hợp API.

Bước 2: Thiết lập Webhook
Bạn cần thiết lập Server với domain HTTPS để đăng ký Webhook nhận sự kiện. Bạn có thể dùng:

Ngrok (dành cho dev local): ngrok http 3000
Render, Railway, Vercel,... (có hỗ trợ HTTPS)
Sau đó sử dụng API setWebhook để thiết lập Webhook cho Zalo Bot của bạn.

Bước 3: Lập trình Bot
Sử dụng Zalo Bot SDK theo code mẫu bên dưới để hiện thực logic cho Bot của bạn.

Python: Tham khảo thêm tài liệu tại python-zalo-bot.
Nodejs: Tham khảo thêm tài liệu tại node-zalo-bot.
Python
Nodejs
from flask import Flask, request
from zalo_bot import Bot, Update
from zalo_bot.ext import Dispatcher, CommandHandler, MessageHandler, filters

TOKEN = 'YOUR_ZALO_BOT_TOKEN'
bot = Bot(token=TOKEN)

app = Flask(__name__)

# Cấu hình webhook 1 lần khi chạy lần đầu
@app.before_first_request
def setup_webhook():
    webhook_url = 'https://your-ngrok-or-domain/webhook'
    bot.set_webhook(url=webhook_url)

# Hàm xử lý /start
def start(update: Update, context):
    update.message.reply_text(f"Xin chào {update.effective_user.first_name}!")

# Hàm xử lý tin nhắn thường
def echo(update: Update, context):
    update.message.reply_text(f"Bạn vừa nói: {update.message.text}")

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

# Gắn dispatcher và handler
from zalo_bot.ext import CallbackContext

dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

if __name__ == '__main__':
    app.run(port=8443)

##3. Hướng dẫn sử dụng Zalo Bot tương tác với Nhóm Chat
Lưu ý
Tính năng đang trong giai đoạn thử nghiệm nội bộ, sẽ được ra mắt trong thời gian tới.

Dưới đây là hướng dẫn chi tiết về cách đưa Zalo Bot vào hoạt động trong môi trường nhóm chat (Group) và quy tắc tương tác giữa thành viên và Bot.

Mục tiêu
Hiểu quy trình mời Bot vào nhóm chat trên Zalo App.
Nắm được cơ chế Bot nhận tin nhắn trong nhóm
Xác định được ID của nhóm để gửi phản hồi.
Bước 1: Chuẩn bị
Trước khi bắt đầu, đảm bảo bạn đã hoàn thành việc tạo Bot và thiết lập môi trường (Webhook hoặc Polling) theo các hướng dẫn trước:

Tạo Bot và lấy Token
Xây dựng Bot với Webhook hoặc Polling
Bước 2: Thêm Bot vào Nhóm Chat
Bot cần được mời vào nhóm chat để có thể tương tác với các thành viên trong nhóm. Thực hiện theo các bước sau để thêm Bot vào nhóm:


Chi tiết các bước:

Lấy Link Bot: Mở Mini app Zalo Bot Creator chọn bot cần thêm vào group để vào trang thông tin của Bot
Chia sẻ vào nhóm: Ở mục "Mời Bot vào nhóm" nhấn nút chia sẻ hoặc gửi link này vào nhóm chat mà bạn muốn thêm Bot.
Kích hoạt: Tại giao diện chat của nhóm, trưởng nhóm nhấn vào link Bot vừa gửi.
Xác nhận: Một popup sẽ hiện ra yêu cầu xác nhận "Thêm Bot vào Nhóm", hãy nhấn Xác nhận.
Hoàn tất: Bot sẽ gửi tin nhắn chào mừng hoặc thông báo đã tham gia nhóm thành công.
Bước 3: Tương tác với Bot trong Nhóm
Sau khi bot được thêm thành công vào group thì các thành viên có thể tương tác với bot theo cách sau.

Các tin nhắn trả lời trực tiếp đến tin nhắn của bot (reply message): Bot sẽ nhận được sự kiện khi có người dùng "Trả lời" (Quote) một tin nhắn mà Bot đã gửi trước đó.
Các tin nhắn mà bot được nhắc đến (mention): Bot sẽ nhận được sự kiện khi người dùng gõ @ và chọn tên của Bot trong tin nhắn.
Xử lý dữ liệu Webhook
Khi sự kiện xảy ra, Bot sẽ nhận được tin nhắn có cấu trúc dữ liệu JSON gửi về Server. Vui lòng tham khảo cấu trúc mẫu tại đây.

Lưu ý khi xử lý:

ID của group sẽ được lấy ở trường chat.id trong dữ liệu nhận về.
Bot có thể sử dụng giá trị chat.id này để gửi API phản hồi tin nhắn vào đúng nhóm chat đó.

# Bảng mã lỗi
Bảng mô tả mã lỗi có thể phát sinh khi sử dụng các APIs của hệ thống. Với các trường hợp lỗi, vui lòng tham khảo thông tin trong trường description trong dữ liệu nhận được để biết thêm chi tiết.

Mã lỗi	Ý nghĩa
400	Bad request - sai đường dẫn hoặc API Name không hợp lệ
401	Unauthorized - Token đã hết hạn hoặc không hợp lệ
403	Internal server error
404	Not found - Yêu cầu truy cập không lệ
408	Request timeout - Quá thời gian xử lý cho phép
429	Quota exceeded - Vượt quá giới hạn sử dụng API cho phép

# Điều khoản sử dụng

ĐIỀU KHOẢN DỊCH VỤ ZALO BOT

I. Giới thiệu
Zalo Bot -- một nền tảng phần mềm của Công ty TNHH Zalo Platforms (sau đây gọi là "Zalo Platforms" hoặc "Chúng tôi") cung cấp công cụ, tính năng kết nối các Dịch vụ Nhà phát triển với Người dùng cuối trên nền tảng ứng dụng Zalo. Nhà phát triển có thể thực hiện nhiều mục đích khác nhau theo nhu cầu của mình, ví dụ dịch vụ chăm sóc khách hàng 24/7, dịch vụ hỏi đáp, cung cấp thông tin cho Người dùng cuối...

Điều khoản Dịch vụ này ("Điều khoản Dịch vụ") là một thỏa thuận pháp lý giữa Nhà phát triển và Zalo Platforms, điều chỉnh việc truy cập, sử dụng Dịch vụ Zalo Bot dưới mọi hình thức. Việc sử dụng Dịch vụ nền tảng đồng nghĩa với việc Nhà phát triển đã đọc, hiểu và đồng ý tuân thủ Điều khoản Dịch vụ này.

II. Định nghĩa
Zalo Bot: Là nền tảng phần mềm được cung cấp bởi Zalo Platforms cho phép Nhà phát triển kết nối, tích hợp Dịch vụ Nhà phát triển với Người dùng cuối trên ứng dụng Zalo.
Dịch vụ Nhà phát triển: là các hệ thống phần mềm do Nhà phát triển tạo và vận hành để tương tác với Người dùng cuối trên nền tảng Zalo thông qua tài khoản Zalo Bot.
Nhà phát triển: Các cá nhân, tổ chức, doanh nghiệp sử dụng Dịch vụ nền tảng để phục vụ các hoạt động kinh doanh, vận hành, chăm sóc khách hàng hoặc các mục đích hợp pháp khác.
Dịch vụ nền tảng hoặc Dịch vụ Zalo Bot: Là các chức năng, giải pháp công nghệ, tiện ích và tính năng liên quan đến Zalo Bot được cung cấp cho Nhà phát triển bởi Zalo Platforms.
Tài khoản Bot: là tài khoản do Nhà phát triển tạo trên nền tảng Zalo nhằm làm giao diện để Người dùng cuối tương tác với phần mềm do Nhà phát triển tạo và vận hành (gọi là "Bot"). Mỗi Nhà phát triển có thể tạo và quản lý một hoặc nhiều Tài khoản Bot như là một phần của Dịch vụ Zalo Bot. Số lượng Tài khoản Bot mà Nhà phát triển có thể tạo và quản lý cùng lúc tùy thuộc vào Gói dịch vụ nền tảng mà Nhà phát triển đã đăng ký.
Gói dịch vụ nền tảng (Subscription Plan): Là gói sử dụng Phiên bản trả phí của Zalo Bot được cung cấp theo chu kỳ thời gian (ví dụ: hàng tháng, hàng quý, hàng năm), với mức phí và tính năng tương ứng. Mỗi gói dịch vụ có thể bao gồm các quyền truy cập khác nhau vào tính năng, hiệu suất hoặc mức độ hỗ trợ, tùy theo chính sách thương mại của Zalo Platforms được công bố tại từng thời điểm.
Chu kỳ thanh toán: Là khoảng thời gian mà Zalo Platforms thu phí dịch vụ đối với Nhà phát triển đã đăng ký Phiên bản trả phí theo Gói dịch vụ. Chu kỳ thanh toán có thể là theo tháng, theo quý, theo năm hoặc theo thời hạn khác được quy định rõ trong từng Gói dịch vụ.
Nội dung tạo sinh: Là mọi thông tin, dữ liệu, kịch bản, âm thanh, văn bản, hình ảnh, câu lệnh hoặc nội dung số khác được Bot tạo ra hoặc chỉnh sửa trong quá trình tương tác, phản hồi với Người dùng cuối.
Người dùng cuối: Là cá nhân tương tác trực tiếp Tài khoản Bot được tạo và quản lý bởi Nhà phát triển thông qua Tài khoản Zalo.
Dữ liệu cá nhân: Là thông tin dưới dạng ký hiệu, chữ viết, chữ số, hình ảnh, âm thanh hoặc dạng tương tự trên môi trường điện tử gắn liền với một con người cụ thể hoặc giúp xác định một con người cụ thể. Dữ liệu cá nhân bao gồm dữ liệu cá nhân cơ bản và dữ liệu cá nhân nhạy cảm.
Zalo hay Nền tảng Zalo: Là nền tảng ứng dụng được sở hữu và vận hành bởi Công ty Cổ phần Tập đoàn VNG.
III. Điều Khoản Sử Dụng
Đăng ký và chấp nhận điều khoản:
Bằng việc truy cập, tải xuống, cài đặt, đăng ký tài khoản hoặc sử dụng bất kỳ thành phần nào của Zalo Bot, Nhà phát triển xác nhận rằng mình đã đọc, hiểu và đồng ý bị ràng buộc bởi toàn bộ nội dung của Điều khoản Dịch vụ này và các chính sách có liên quan do Zalo Platforms công bố trên các nền tảng do Zalo Platforms sở hữu hoặc quản lý hoặc theo phương thức khác mà Zalo Platforms thấy phù hợp.
Nếu Nhà phát triển không đồng ý với bất kỳ nội dung nào trong Điều khoản Dịch vụ, vui lòng ngừng sử dụng Zalo Bot. Việc tiếp tục sử dụng Zalo Bot được hiểu là sự chấp thuận rõ ràng và không điều kiện đối với toàn bộ Điều khoản Dịch vụ này.
Zalo Platforms bảo lưu quyền sửa đổi, cập nhật hoặc thay thế toàn bộ hoặc một phần nội dung của Điều khoản Dịch vụ này theo quy định tại Điều XI Điều khoản Dịch vụ này.
Đồng thời, trong quá trình sử dụng Dịch vụ nền tảng, triển khai Bot và tương tác với Người dùng cuối, Nhà phát triển có thể sử dụng dịch vụ bên thứ ba (ví dụ các phần mềm, cơ sở dữ liệu, nền tảng hoặc hệ thống trí tuệ nhân tạo..), do đó Nhà phát triển cam kết sẽ đọc, hiểu và tuân thủ theo các chính sách được ban hành và cập nhật liên tục bởi dịch vụ bên thứ ba này. Nhà phát triển tự chịu trách nhiệm trong việc tuân thủ các chính sách này và đảm bảo Zalo Platforms được miễn trừ với mọi thiệt hại, chi phí phát sinh từ việc vi phạm các chính sách này do lỗi của Nhà phát triển.
Nhà phát triển chịu trách nhiệm bảo mật thông tin đăng nhập của mình vào nền tảng Zalo Bot để sử dụng Dịch vụ nền tảng và thông báo kịp thời nếu phát hiện có bất kỳ hoạt động sử dụng trái phép nào.
Năng lực hành vi
Zalo Bot chỉ được cung cấp cho Nhà phát triển là cá nhân từ đủ mười tám (18) tuổi trở lên và có đầy đủ năng lực hành vi dân sự theo quy định của pháp luật Việt Nam, hoặc tổ chức được thành lập và hoạt động hợp pháp theo pháp luật. Trường hợp Nhà phát triển từ đủ mười ba (13) tuổi đến dưới mười tám (18) tuổi, việc sử dụng Zalo Bot phải có sự đồng ý và giám sát của cha, mẹ hoặc người giám hộ hợp pháp.
Zalo Platforms không chịu trách nhiệm nếu Nhà phát triển khai báo thông tin không chính xác hoặc sử dụng Zalo Bot khi không đủ điều kiện về độ tuổi hoặc năng lực hành vi theo quy định nêu trên.
Quyền sử dụng Dịch vụ nền tảng:
Dịch vụ nền tảng Zalo Bot được Zalo Platforms công bố và điều chỉnh theo từng thời kỳ tại website Zalo Bot Platform.
Zalo Platforms toàn quyền quyết định kiến trúc kỹ thuật, tính năng, giao diện, phạm vi và chính sách vận hành của Zalo Bot, bao gồm việc sửa đổi, bổ sung hoặc ngừng cung cấp một phần hoặc toàn bộ Dịch vụ nền tảng.
Zalo Bot được cung cấp cho Nhà phát triển "nguyên trạng" ("as is") và "theo khả năng hiện có" ("as available"), không kèm theo bất kỳ cam kết hoặc bảo đảm nào -- dù rõ ràng hay ngụ ý -- về hiệu suất, tính chính xác, tính phù hợp hoặc kết quả sử dụng.
Trong phạm vi pháp luật cho phép, Zalo Platforms từ chối tất cả các bảo đảm rõ ràng hoặc ngụ ý, bao gồm nhưng không giới hạn ở:
Bảo đảm về tính thương mại, tính phù hợp với một mục đích cụ thể hoặc tính không vi phạm quyền của bên thứ ba;
Bảo đảm liên quan đến tính liên tục, độ tin cậy, hiệu suất hoặc kết quả từ việc sử dụng Zalo Bot.
Chúng tôi cung cấp cho Nhà phát triển quyền sử dụng Dịch vụ nền tảng theo dạng không độc quyền, không chuyển nhượng và chỉ được sử dụng cho mục đích kinh doanh hợp pháp.
Nhà phát triển không được sử dụng Dịch vụ nền tảng với mục đích vi phạm pháp luật, xâm phạm quyền của người khác, hay gây thiệt hại đến hệ thống và danh tiếng.
Nhà phát triển thừa nhận và đồng ý rằng Zalo Platforms chỉ cung cấp nền tảng, phần mềm mang tính kỹ thuật thuần túy để Nhà phát triển kết nối, tích hợp các Bot của Nhà phát triển đến nền tảng Zalo; Zalo Platforms không liên quan, không tham gia vào quan hệ, giao dịch hay cam kết nào giữa Nhà phát triển và Người dùng cuối, bất kể rõ ràng hay ngầm định, và không cung cấp tư vấn chuyên môn hay dịch vụ thay mặt Nhà phát triển.
Zalo Platforms có quyền bảo trì, nâng cấp, thử nghiệm hoặc triển khai biện pháp kỹ thuật để bảo vệ hệ thống Zalo Bot, Nhà phát triển và Người dùng cuối; có thể tạm ngừng Dịch vụ nền tảng trong thời gian cần thiết; có quyền áp dụng ngay biện pháp kỹ thuật hoặc hạn chế truy cập khi phát hiện hoặc nghi ngờ có rủi ro an ninh mạng, tấn công hệ thống, gian lận hoặc vi phạm pháp luật.
Khi tự phát hiện những hành vi vi phạm hoặc nhận được thông báo vi phạm về nội dung cấm được quy định tại Điều khoản Dịch vụ này bởi Nhà phát triển, Zalo Platforms có quyền ngay lập tức gỡ bỏ, và/hoặc cảnh cáo, khóa, tạm dừng Dịch vụ nền tảng cung cấp cho Nhà phát triển nhằm điều tra, đánh giá và xử lý vi phạm. Zalo Platforms có toàn quyền quyết định các hình thức xử lý đối với các trường hợp vi phạm. Tuy vào tính chất sự việc, mức độ ảnh hưởng và nghiêm trọng, Zalo Platforms sẽ đưa ra hình thức xử lý phù hợp. Nhà phát triển đồng ý và xác nhận tuân theo các quyết định của Zalo Platforms.
Điều khoản thanh toán và phí Dịch vụ nền tảng

a. Dịch vụ miễn phí và Dịch vụ trả phí

Dịch vụ Zalo Bot được cung cấp dưới hai hình thức Phiên bản miễn phí (Free Version) và Phiên bản trả phí (Premium Version). Trong đó, Nhà phát triển đăng ký Gói dịch vụ nền tảng có thu phí theo Chu kỳ thanh toán tương ứng để sử dụng các tính năng nâng cao, cải tiến hiệu suất hoặc được ưu tiên hỗ trợ của Phiên bản trả phí.

Ngoài phí sử dụng Gói dịch vụ nền tảng, Nhà phát triển có thể phát sinh thêm các loại phí dịch vụ khác tùy theo chức năng sử dụng. Tất cả các loại phí bổ sung sẽ được công bố rõ ràng trước khi phát sinh nghĩa vụ thanh toán, và chỉ có hiệu lực khi Nhà phát triển đồng ý.

Thông tin chi tiết về Gói dịch vụ nền tảng, bao gồm phạm vi tính năng, giá cước, Chu kỳ thanh toán và điều kiện sử dụng, và các loại phí dịch vụ khác sẽ được công bố công khai bởi Zalo Platforms trên nền tảng chính thức của Zalo Bot.

b. Phương thức thanh toán:

Nhà phát triển có thể thực hiện thanh toán thông qua một trong các phương thức được Zalo Platforms hỗ trợ tại từng thời điểm, bao gồm nhưng không giới hạn ở:

Ví điện tử, thẻ tín dụng/thẻ ghi nợ, tài khoản ngân hàng liên kết;
Tính năng thanh toán trong ứng dụng hoặc thông qua nền tảng bên thứ ba được tích hợp với Zalo Bot;
Hệ thống thanh toán qua thiết bị hỗ trợ Zalo Bot, nếu có.
Việc thanh toán được xem là hoàn tất khi hệ thống của Zalo Platforms xác nhận đã nhận được số tiền tương ứng.

c. Gia hạn và hủy Gói dịch vụ

Thanh toán định kỳ: Trừ khi được quy định khác tại thời điểm đăng ký, các Gói dịch vụ nền tảng được thanh toán định kỳ (theo tháng, quý, năm...) sẽ tự động gia hạn và thanh toán vào đầu mỗi Chu kỳ thanh toán, trừ khi Nhà phát triển chủ động hủy gia hạn.

Nhà phát triển có thể hủy gia hạn thông qua giao diện quản lý tài khoản hoặc theo hướng dẫn của Zalo Platforms.

Việc hủy gia hạn được hiểu rằng Nhà phát triển sẽ không tiếp tục thanh toán cho Chu kỳ thanh toán tiếp theo. Theo đó, Nhà phát triển vẫn có thể dùng Gói dịch vụ nền tảng đến hết thời gian đã được thanh toán.

Thanh toán một lần: Các Gói dịch vụ nền tảng được thanh toán một lần (ví dụ: mua theo gói 6 tháng, 1 năm) sẽ tự động kết thúc khi hết thời hạn đã được thanh toán.

Quy định chung về Hủy dịch vụ: Nhà phát triển có thể hủy Gói dịch vụ vào bất kỳ thời điểm nào, tuy nhiên sẽ không được hoàn tiền cho phần thời gian còn lại trong Chu kỳ thanh toán đã bắt đầu, trừ trường hợp được quy định tại chính sách hoàn tiền của Zalo Platforms.

d. Chính sách hoàn tiền

Trừ khi có quy định rõ ràng khác từ Zalo Platforms hoặc theo luật định, Zalo Platforms không có nghĩa vụ hoàn tiền sau khi một Chu kỳ thanh toán đã bắt đầu, bao gồm cả các trường hợp:

Nhà phát triển không sử dụng Dịch vụ nền tảng trong suốt thời gian đã đăng ký;
Nhà phát triển vô tình đăng ký hoặc không nhận thấy gia hạn tự động;
Nhà phát triển bị chấm dứt quyền sử dụng, chấm dứt tài khoản hoặc bị cấm sử dụng Dịch vụ nền tảng của Zalo Bot do vi phạm Điều khoản này.
Trường hợp việc hoàn tiền là bắt buộc theo quy định pháp luật, Zalo Platforms sẽ thực hiện theo hình thức và thời gian được quy định tại chính sách hoàn tiền công khai.

e. Từ chối thanh toán và gian lận

Zalo Platforms có quyền tạm ngưng hoặc chấm dứt quyền truy cập Dịch vụ nền tảng của Nhà phát triển trong các trường hợp sau:

Có dấu hiệu Nhà phát triển sử dụng phương thức thanh toán không hợp lệ, từ chối thanh toán sau khi giao dịch đã hoàn tất, hoặc thực hiện hành vi gian lận trong quá trình thanh toán;
Nhà phát triển vi phạm bất kỳ nội dung nào của Điều khoản Dịch vụ này, bao gồm nhưng không giới hạn ở: sử dụng trái phép Zalo Bot, sử dụng Bot vi phạm pháp luật, hoặc vi phạm quy định về các hành vi bị cấm;
Có yêu cầu hợp lệ từ cơ quan Nhà nước có thẩm quyền hoặc theo quy định pháp luật hiện hành.
Trong các trường hợp nêu trên, Nhà phát triển không có quyền yêu cầu hoàn tiền cho phần Dịch vụ nền tảng còn lại (nếu có), và Zalo Platforms có quyền thu thêm các khoản phí xử lý tổn thất (nếu có) phát sinh do hành vi vi phạm.

Tạo và quản lý tài khoản
Để sử dụng Dịch vụ Zalo Bot, Nhà phát triển cần có tài khoản Zalo trên Nền tảng Zalo.
Là một phần của Dịch vụ nền tảng, Zalo Platforms cung cấp giải pháp cho Nhà phát triển sử dụng tài khoản Zalo của Nhà phát triển để tạo Tài khoản Bot tương tác với Người dùng cuối trên nền tảng Zalo. (Nhà phát triển tham khảo chi tiết tại trang https://bot.zaloplatforms.com/docs/create-bot) (sau đây gọi là "Tài khoản Nhà phát triển" và "Tài khoản Bot")
Nhà phát triển có trách nhiệm bảo mật thông tin đăng nhập và mọi hoạt động diễn ra thông qua Tài khoản Nhà phát triển của mình. Trong mọi trường hợp, mọi hành vi truy cập hoặc sử dụng Zalo Bot từ Tài khoản Nhà phát triển sẽ được xem là hành vi của chính chủ tài khoản (cá nhân chủ số điện thoại đăng ký tài khoản Zalo), trừ khi có chứng cứ xác thực chứng minh hành vi trái phép và đã thông báo kịp thời cho Zalo Platforms theo quy định tại Điều khoản Dịch vụ này.
Zalo Platforms không chịu trách nhiệm đối với bất kỳ tổn thất, thiệt hại hoặc hậu quả nào phát sinh từ việc Nhà phát triển không bảo mật tài khoản, chia sẻ thông tin truy cập, hoặc không thông báo kịp thời khi phát hiện có hành vi sử dụng trái phép.

Zalo Platforms có quyền, theo quyết định riêng của mình và không cần thông báo trước, tạm ngưng, giới hạn hoặc chấm dứt Tài khoản Nhà phát triển và/hoặc Tài khoản Bot trong các trường hợp sau:
Vi phạm bất kỳ quy định nào trong Điều khoản Dịch vụ này;
Sử dụng Zalo Bot trái với pháp luật hoặc gây ảnh hưởng đến quyền lợi hợp pháp của Zalo Platforms hoặc bên thứ ba;
Có hành vi gian lận, gây rối hệ thống, hoặc làm ảnh hưởng đến sự ổn định của Dịch vụ nền tảng;
Tài khoản có chứa, phát tán, lưu trữ, chia sẻ hoặc sử dụng thông tin sai lệch, vi phạm thuần phong mỹ tục, trái đạo đức xã hội, hoặc xâm phạm quyền và lợi ích hợp pháp của cá nhân, tổ chức khác;
Các trường hợp Zalo Platforms được quyền chấm dứt Dịch vụ nền tảng theo Điều khoản Dịch vụ này; hoặc
Có yêu cầu từ cơ quan có thẩm quyền.
Trong trường hợp Tài khoản Nhà phát triển và/hoặc Tài khoản Bot bị tạm ngưng hoặc chấm dứt theo Điều khoản Dịch vụ này, Nhà phát triển và Người dùng cuối có thể mất quyền truy cập vào các dữ liệu, nội dung, hoặc gói Dịch vụ đã đăng ký. Zalo Platforms không chịu trách nhiệm về việc khôi phục dữ liệu trong các trường hợp này.
Nhà phát triển và trách nhiệm sử dụng:
Nhà phát triển hiểu rằng mình là nhà cung cấp, bên nhập khẩu và/hoặc bên triển khai hệ thống trí tuệ nhân tạo, do đó, Nhà phát triển cam kết chịu mọi trách nhiệm trước pháp luật và đảm bảo thực hiện mọi nghĩa vụ tuân thủ theo quy định đối với nhà cung cấp, bên nhập khẩu và/hoặc bên triển khai hệ thống trí tuệ nhân tạo.
Nhà phát triển tự chịu trách nhiệm toàn bộ đối với nội dung, thông tin, dữ liệu và các hoạt động tương tác với Người dùng cuối được thực hiện thông qua Tài khoản Bot, bao gồm nhưng không giới hạn ở nội dung tin nhắn, kịch bản, dữ liệu truyền dẫn và phản hồi tự động. Zalo Platforms không chịu trách nhiệm đối với bất kỳ vi phạm, tranh chấp, rủi ro hoặc khiếu nại nào phát sinh từ các nội dung hoặc hành vi của Nhà phát triển.
Trường hợp Nhà phát triển sử dụng dịch vụ bên thứ ba thì phải có trách nhiệm thiết lập, duy trì và thực thi các biện pháp kỹ thuật và quản lý hợp lý nhằm kiểm soát và ngăn chặn các vi phạm hoặc thực hiện hành vi bị cấm, vi phạm quy định pháp luật hoặc Điều khoản Dịch vụ này; kịp thời vô hiệu hóa, hạn chế hoặc đình chỉ truy cập/sử dụng dịch vụ bên thứ ba khi phát hiện hoặc có căn cứ hợp lý nghi ngờ, đồng thời thực hiện ngay các biện pháp khắc phục phù hợp; thông báo ngay cho Zalo Platforms qua kênh hỗ trợ được chỉ định không muộn hơn 24 giờ kể từ thời điểm phát hiện, kèm các thông tin tối thiểu: mô tả sự kiện, thời điểm phát hiện, phạm vi ảnh hưởng, loại dữ liệu/Nội dung tạo sinh liên quan, biện pháp đã thực hiện.
Nhà phát triển cam kết và hoàn toàn chịu trách nhiệm trước pháp luật và trước Zalo Platforms đối với:
Việc đảm bảo tính chính xác, trung thực, hợp pháp của dữ liệu, thông tin cung cấp cho Người dùng cuối;
Đảm bảo mục đích của Dịch vụ Nhà phát triển hợp pháp, phục vụ nhu cầu của Người dùng cuối và không vi phạm pháp luật, đạo đức xã hội;
Đảm bảo Người dung cuối nhận thức được họ đang tương tác với một hệ thống phần mềm tự động, thông báo cáo hành vi bị cấm, thông báo về việc có thu thập, xử lý dữ liệu người dùng hay không, đồng thời áp dụng biện pháp kỹ thuật để gắn nhãn Nội dung tạo sinh hoặc định danh rõ ràng theo một định dạng máy có thể đọc được.
Zalo Platforms có quyền (nhưng không có nghĩa vụ) theo dõi, kiểm tra, chặn, chỉnh sửa, xóa bỏ hoặc báo cáo cho cơ quan có thẩm quyền bất kỳ Nội dung tạo sinh nào nếu có dấu hiệu:
Vi phạm quy định pháp luật hoặc Điều khoản Dịch vụ này;
Ảnh hưởng đến an toàn của hệ thống hoặc quyền lợi của Zalo Platforms, Nhà phát triển khác hoặc bên thứ ba.
Việc không thực hiện các hành động này không được hiểu là Zalo Platforms đồng ý hoặc miễn trừ trách nhiệm của Nhà phát triển đối với Nội dung đã cung cấp.
Nhà phát triển bảo đảm có đầy đủ quyền và giấy phép đối với mọi dữ liệu, kịch bản, tập huấn luyện, prompt, tài liệu, nhãn hiệu, tác phẩm, hình ảnh, âm thanh, video... đưa vào Dịch vụ nền tảng, và việc sử dụng không xâm phạm quyền sở hữu trí tuệ của bất kỳ bên nào.
Nhà phát triển có trách nhiệm thông báo kịp thời cho Zalo Platforms về bất kỳ sự cố an ninh, rò rỉ dữ liệu, vi phạm chính sách hoặc khiếu nại đáng kể nào liên quan đến việc sử dụng Dịch vụ Nhà phát triển.
Nhà phát triển có trách nhiệm thông báo cho Người dùng cuối trước khi Người dùng cuối bắt đầu tương tác Tài khoản Bot và tự chịu trách nhiệm pháp lý đối với bất kỳ thiệt hại nào phát sinh từ:
Việc Người dùng cuối tạo, cung cấp hoặc chia sẻ Nội dung tạo sinh không phù hợp, sai lệch hoặc vi phạm pháp luật;
Việc sử dụng Nội dung tạo sinh mà không kiểm chứng, hoặc áp dụng trong các bối cảnh chuyên môn đòi hỏi đánh giá của con người;
Hành vi của bất kỳ bên thứ ba nào truy cập, sử dụng Nội dung tạo sinh một cách trái phép, kể cả khi xảy ra qua nền tảng của Zalo Bot.
Sử dụng và tích hợp:
Zalo Platforms không chịu trách nhiệm đối với các lỗi hoặc giới hạn phát sinh từ thiết bị không tương thích, sự cố mạng, hoặc hạ tầng kỹ thuật không đáp ứng yêu cầu.
Dịch vụ nền tảng được cung cấp nhằm hỗ trợ tích hợp Dịch vụ Nhà phát triển một cách dễ dàng trên nền tảng Zalo. Nhà phát triển cam kết tuân thủ các quy định, chính sách liên quan đến ứng dụng Zalo và bất kỳ chính sách nào khác có liên quan được ban hành và công bố bởi Công ty Cổ phần Tập đoàn VNG.
IV. Quyền Sở Hữu Trí Tuệ
Sở hữu phần mềm và nội dung:
Zalo Bot là dịch vụ, phần mềm, giải pháp được phát triển và vận hành bởi Zalo Platforms và được bảo hộ theo pháp luật Việt Nam và các điều ước quốc tế liên quan đến quyền sở hữu trí tuệ. Toàn bộ quyền, quyền sở hữu và lợi ích liên quan đến Zalo Bot -- bao gồm nhưng không giới hạn: phần mềm, mã nguồn, hệ thống thuật toán, giao diện nhà phát triển, thiết kế, dữ liệu, tài liệu kỹ thuật, nội dung tích hợp, hình ảnh, âm thanh, cũng như mọi bản cập nhật, nâng cấp hoặc bản phái sinh -- đều thuộc quyền sở hữu hợp pháp của Zalo Platforms hoặc các bên được Zalo Platforms cấp phép hợp pháp.
Không nội dung nào trong Điều khoản Dịch vụ này sẽ được hiểu là việc chuyển nhượng, cấp phép ngầm định, hay từ bỏ bất kỳ quyền sở hữu trí tuệ nào của Zalo Platforms đối với Zalo Bot hoặc bất kỳ phần nào của sản phẩm. Mọi quyền không được cấp rõ ràng cho Nhà phát triển theo Điều khoản Dịch vụ này đều được Zalo Platforms bảo lưu.
Zalo Platforms cấp cho Nhà phát triển một quyền sử dụng có giới hạn, không độc quyền, không chuyển nhượng, không cấp phép lại và có thể bị thu hồi để truy cập và sử dụng Zalo Bot theo mục đích phù hợp với quy định pháp luật và Điều khoản Dịch vụ này.
Nhà phát triển không được phép, trừ khi có sự đồng ý trước bằng văn bản của Zalo Platforms :
Sao chép, chỉnh sửa, tái bản, phân phối lại, cấp phép lại, bán hoặc cho thuê bất kỳ phần nào của Zalo Bot;
Thực hiện kỹ thuật đảo ngược (reverse engineer), biên dịch ngược (decompile), phân tách, tháo rời hoặc cố gắng truy xuất mã nguồn hoặc cấu trúc nội bộ của Zalo Bot;
Sử dụng Zalo Bot để tạo ra sản phẩm, Dịch vụ hoặc mô hình cạnh tranh với Zalo Bot hoặc với Zalo Platforms ;
Truy cập trái phép vào hệ thống, API hoặc tài nguyên nội bộ của Zalo Bot.
Tất cả nhãn hiệu, tên thương mại, biểu tượng, tên sản phẩm và Dịch vụ nền tảng liên quan đến Zalo Bot là tài sản của Zalo Platforms hoặc bên cấp phép tương ứng và được bảo hộ theo quy định pháp luật hiện hành. Nhà phát triển không được sử dụng các tài sản này cho bất kỳ mục đích nào mà không có sự cho phép trước bằng văn bản của Zalo Platforms. Nhà phát triển không được sao chép, chỉnh sửa, chuyển giao hay khai thác dưới bất kỳ hình thức nào nếu không có sự cho phép bằng văn bản.
Bản quyền Nội dung tạo sinh:
Nhà phát triển giữ bản quyền đối với nội dung mà họ tự tạo ra và đăng tải lên hệ thống, tuy nhiên, việc sử dụng Dịch vụ nền tảng có thể yêu cầu cấp phép không độc quyền cho Chúng tôi sử dụng Nội dung tạo sinh nhằm mục đích vận hành và cải thiện Dịch vụ nền tảng.

V. Bảo Mật Và Bảo Vệ Dữ Liệu
Xử lý dữ liệu
Bằng việc sử dụng Zalo Bot, Nhà phát triển xác nhân và đồng ý rằng Zalo Platforms có quyền áp dụng những biện pháp kỹ thuật cho mục đích thu thập và xử lý các dữ liệu liên quan nhằm phục vụ Nhà phát triển. Tùy từng trường hợp, Chúng tôi có thể thực hiện thu thập và xử lý dữ liệu cá nhân của Nhà phát triển cụ thể như sau:

Dữ liệu dự kiến được xử lý trong việc cung cấp Zalo Bot:
Thông tin thiết bị: thông tin hệ điều hành, thông tin phần mềm của Nhà phát triển (tên gọi, chức năng, phiên bản, mục đích, mức độ rủi ro), ngôn ngữ sử dụng và thông số mạng;
Thông tin do Nhà phát triển tự nguyện, chủ động cung cấp cho Chúng tôi: Các dữ liệu trên có thể được Nhà phát triển xác nhận chủ động cung cấp thông qua các biểu mẫu phản hồi, yêu cầu hỗ trợ hoặc các hình thức liên hệ khác (nếu có) khi Nhà phát triển sử dụng Dịch vụ nền tảng. Chúng tôi không khuyến khích hay yêu cầu Nhà phát triển phải cung cấp ngoài những dữ liệu cần thiết hợp pháp nhằm phục vụ cho hoạt động hỗ trợ Nhà phát triển.
Với mục tiêu bảo vệ quyền riêng tư, đảm bảo tính bảo mật và tuân thủ đầy đủ các quy định pháp luật hiện hành, Chúng tôi cam kết toàn bộ dữ liệu đều được mã hóa trong suốt quá trình xử lý. Bên cạnh đó, Chúng tôi áp dụng các biện pháp bảo mật nghiêm ngặt và triển khai các phương thức kỹ thuật phù hợp nhằm duy trì trạng thái ẩn danh của thông tin, đảm bảo rằng dữ liệu không thể được liên kết trực tiếp hoặc gián tiếp với bất kỳ cá nhân cụ thể nào.

Mục đích xử lý dữ liệu
Zalo Platforms xử lý dữ liệu thu thập được từ Zalo Bot cho các mục đích sau:

Cung cấp, duy trì và tối ưu hoá Dịch vụ nền tảng: Đảm bảo việc cung cấp Dịch vụ nền tảng được thực hiện một cách ổn định, liên tục, phù hợp và an toàn cho toàn bộ Nhà phát triển khi sử dụng Zalo Bot của Zalo Platforms trên nền tảng Zalo.
Liên lạc và hỗ trợ Nhà phát triển: Bao gồm tiếp nhận và xử lý phản hồi, gửi thông báo liên quan đến cập nhật Dịch vụ nền tảng, cũng như cung cấp hỗ trợ kỹ thuật khi cần thiết.
Tuân thủ quy định pháp luật: Đáp ứng các yêu cầu từ cơ quan Nhà nước có thẩm quyền theo đúng quy định của pháp luật hiện hành.
Phương thức xử lý dữ liệu
Lưu trữ: Dữ liệu có thể được lưu trữ trên hệ thống máy chủ thuộc quyền kiểm soát của Zalo Platforms tại lãnh thổ nước Cộng hòa xã hội chủ nghĩa Việt Nam.
Bảo mật: Zalo Platforms áp dụng các biện pháp bảo mật kỹ thuật và tổ chức phù hợp để ngăn chặn truy cập trái phép, rò rỉ, thay đổi hoặc hủy hoại dữ liệu, bao gồm mã hóa, kiểm soát truy cập, giám sát hệ thống và chính sách nội bộ. Mặc dù vậy, các rủi ro liên quan đến việc cung cấp, bảo mật dữ liệu cá nhân, cho dù là cung cấp trực tiếp, qua điện thoại hay qua mạng Internet hay qua các phương tiện kỹ thuật sẽ luôn tiềm ẩn và không có hệ thống kỹ thuật hay biên pháp an ninh, bảo mật nào là an toàn tuyêt đối hay có thể chống lại được tất cả các "hacker", "tamper" (những người xâm nhập trái phép để lục lọi thông tin). Do đó, trong trường hợp dữ liệu cá nhân của Nhà phát triển bị lộ do bị tấn công mạng hoặc các nguyên nhân khác nằm ngoài tầm kiểm soát của Zalo Platforms thì Nhà phát triển theo đây xác nhận và đồng ý rằng Zalo Platforms được miễn trừ toàn bộ trách nhiệm có liên quan.
Chia sẻ dữ liệu: Zalo Platforms không chia sẻ dữ liệu cá nhân của Nhà phát triển cho bên thứ ba ngoại trừ các trường hợp:
Chia sẻ hoặc nhận chia sẻ với các công ty trực thuộc Công ty Cổ phần Tập đoàn VNG bao gồm công ty con, công ty thành viên, công ty liên kết của Công ty Cổ phần Tập đoàn VNG vì một hay nhiều mục đích đã được thông báo tới Nhà phát triển.
Có sự xác nhận và đồng ý rõ ràng từ Nhà phát triển và/hoặc để thực hiện các chức năng hoặc Dịch vụ nền tảng mà Nhà phát triển yêu cầu;
Theo yêu cầu từ cơ quan nhà nước có thẩm quyền phù hợp với quy định của pháp luật;
Cho phép các đối tác thực hiện các chức năng được ủy quyền chính thức bởi Zalo Platforms (ví dụ: lưu trữ và xử lý dữ liệu), với điều kiện các bên liên quan phải tuân thủ các chính sách và tiêu chuẩn bảo mật tương đương với những quy định do Zalo Platforms áp dụng.
Quyền của Nhà phát triển
Nhà phát triển, với tư cách là chủ thể dữ liệu, có các quyền của chủ thể dữ liệu cá nhân theo quy định của pháp luật.
Trong trường hợp Nhà phát triển có bất kỳ câu hỏi nào liên quan đến Quy định bảo vệ dữ liệu cá nhân hoặc các vấn đề liên quan đến quyền của Chủ thể dữ liệu hoặc xử lý dữ liệu cá nhân của Nhà phát triển, Nhà phát triển vui lòng liên hệ trực tiếp tại địa chỉ: Tầng 2, Tòa nhà Saigon Paragon, số 3 Nguyễn Lương Bằng, Phường Tân Mỹ, Thành phố Hồ Chí Minh, Việt Nam.
Zalo Platforms có thể yêu cầu Nhà phát triển thực hiện các bước xác minh danh tính trước khi xử lý các yêu cầu liên quan đến quyền của Nhà phát triển, nhằm bảo đảm việc tuân thủ quy định pháp luật hiện hành cũng như phòng ngừa rủi ro và hạn chế phát sinh tranh chấp (nếu có).
Các quyền của chủ thể dữ liệu theo Nghị định 13/2023/NĐ-CP và/hoặc các văn bản pháp luật liên quan tới dữ liệu, cụ thể như sau:
Quyền được biết: Nhà phát triển được biết về hoạt động xử lý dữ liệu cá nhân của mình, trừ trường hợp luật có quy định khác.
Quyền đồng ý: Nhà phát triển được đồng ý hoặc không đồng ý cho phép xử lý dữ liệu cá nhân của mình, trừ trường hợp quy định tại Điều 17 Nghị định.
Quyền truy cập: Nhà phát triển được truy cập để xem, chỉnh sửa hoặc yêu cầu chỉnh sửa dữ liệu cá nhân của mình, trừ trường hợp luật có quy định khác.
Quyền rút lại sự đồng ý: Nhà phát triển được quyền rút lại sự đồng ý của mình, trừ trường hợp luật có quy định khác.
Quyền xóa dữ liệu: Nhà phát triển được xóa hoặc yêu cầu xóa dữ liệu cá nhân của mình, trừ trường hợp luật có quy định khác.
Quyền cung cấp dữ liệu: Nhà phát triển được yêu cầu Bên Kiểm soát dữ liệu cá nhân, Bên Kiểm soát và xử lý dữ liệu cá nhân cung cấp cho bản thân dữ liệu cá nhân của mình, trừ trường hợp luật có quy định khác.
Quy định khác về hoạt động xử lý dữ liệu
Xét về vai trò, Zalo Platforms chỉ là nhà cung cấp nền tảng/phần mềm mang tính kỹ thuật thuần túy và không tham gia, không đồng kiểm soát, không đưa ra bất kỳ hướng dẫn, chỉ đạo Nhà phát triển trong việc xử lý Dữ liệu cá nhân đối với Người dùng cuối. Nhà phát triển cam kết chịu trách nhiệm với mọi hoạt động xử lý Dữ liệu cá nhân mà mình đang thực hiện thông qua Zalo Bot hoặc trong quá trình sử dụng Dịch vụ nền tảng.
Nhà phát triển chịu mọi trách nhiệm trong toàn bộ hoặc một phần bất kỳ hoạt động xử lý Dữ liệu cá nhân của Nhà phát triển thông qua Zalo Bot hoặc trong quá trình sử dụng Dịch vụ nền tảng, bao gồm nhưng không giới hạn các trách nhiệm thông báo trước Người dùng cuối, chủ thể dữ liệu, Cơ quan chuyên trách bảo vệ Dữ liệu cá nhân về các thiệt hại do quá trình xử lý Dữ liệu cá nhân gây ra và bảo vệ Zalo Platforms khỏi các bất lợi, trách nhiệm liên quan, ngoại trừ trường hợp có quy định khác.
Trong phạm vi pháp luật cho phép, Nhà phát triển đảm bảo Zalo Platforms được miễn trừ mọi trách nhiệm và cam kết bồi thường; được bảo vệ trước mọi khiếu nại, tranh chấp, xử phạt, chi phí và phí luật sư phát sinh từ hoặc liên quan đến (i) việc Nhà phát triển thu thập, sử dụng, chia sẻ, lưu trữ hay xử lý dữ liệu của các chủ thể liên quan. Người dùng cuối; (ii) Nội dung, thông tin do Nhà phát triển khởi tạo/thiết lập/cung cấp vào Zalo Bot hoặc sử dụng cho Bot (bao gồm dữ liệu, thông tin, kịch bản, câu lệnh, văn bản, âm thanh, hình ảnh, video); và/hoặc (iii) mọi tranh chấp, khiếu nại, trách nhiệm pháp lý giữa Nhà phát triển và Người dùng cuối các bên liên quan về dữ liệu cá nhân.
Tài liệu và các chính sách liên quan
Mọi hoạt động xử lý dữ liệu giữa Zalo Platforms và Nhà phát triển và/hoặc các bên liên quan khác sẽ được điều chỉnh và thực hiện theo các điều khoản, quy định tại Thoả Thuận Xử Lý Dữ Liệu Công Khai của Zalo Platforms tại: https://miniapp.zaloplatforms.com/documents/zalo-mini-app-developer-program-agreement/public-dpa.

Ngoài các quy định cụ thể tại Điều khoản Dịch vụ này, việc thu thập, sử dụng và bảo vệ dữ liệu cá nhân của Nhà phát triển được quy định chi tiết trong Thỏa thuận sử dụng dịch vụ Zalo của Công ty Cổ phần Tập đoàn VNG tại https://zalo.vn/dieukhoan và Thoả thuận sử dụng Dịch vụ Zalo Platforms của Công ty TNHH Zalo Platforms tại https://miniapp.zaloplatforms.com/documents/zalo-mini-app-developer-program-agreement/ được cập nhật theo từng thời kỳ. Thoả thuận này là một phần không tách rời khỏi Thoả thuận sử dụng dịch vụ Zalo.

Nhà phát triển có trách nhiệm đọc kỹ Thỏa thuận sử dụng dịch vụ Zalo để hiểu rõ quyền và nghĩa vụ của mình liên quan đến việc xử lý dữ liệu cá nhân. Việc tiếp tục truy cập hoặc sử dụng Zalo Bot sẽ được hiểu là sự xác nhận và chấp thuận rõ ràng, đầy đủ của Nhà phát triển đối với toàn bộ nội dung được quy định trong Thỏa thuận sử dụng dịch vụ Zalo, bao gồm việc Zalo Platforms tiến hành xử lý dữ liệu cá nhân theo chính sách đó.

VI. Giới Hạn Trách Nhiệm
Tuyên bố miễn trừ bảo đảm
Trong phạm vi pháp luật cho phép, Zalo Platforms từ chối tất cả các bảo đảm rõ ràng hoặc ngụ ý, bao gồm nhưng không giới hạn ở:
Bảo đảm về tính thương mại, tính phù hợp với một mục đích cụ thể hoặc tính không vi phạm quyền của bên thứ ba;
Bảo đảm liên quan đến tính liên tục, độ tin cậy, hiệu suất hoặc kết quả từ việc sử dụng Zalo Bot.
Nhà phát triển hoàn toàn chịu trách nhiệm đối với:
Mọi hành động, quyết định hoặc hệ quả (bao gồm nhưng không giới hạn ở tổn thất tài chính, hậu quả pháp lý hoặc ảnh hưởng tinh thần) phát sinh từ việc sử dụng Zalo Bot;

Việc không tham khảo ý kiến từ các chuyên gia trong những lĩnh vực đòi hỏi tư vấn chuyên môn, chính thống hoặc được cấp phép hành nghề.

Tuyên bố giới hạn trách nhiệm pháp lý
Trong mọi trường hợp, Zalo Platforms và các bên liên quan không chịu trách nhiệm pháp lý đối với bất kỳ thiệt hại nào phát sinh từ hoặc liên quan đến việc sử dụng hoặc không thể sử dụng Zalo Bot, bao gồm nhưng không giới hạn ở:
Thiệt hại trực tiếp, gián tiếp, ngẫu nhiên, đặc biệt, mang tính hệ quả hoặc mất mát về thu nhập, dữ liệu hoặc uy tín;
Mọi thiệt hại phát sinh từ hành vi hoặc nội dung của Nhà phát triển hoặc bên thứ ba hoặc Nội dung tạo sinh;
Việc sử dụng Dịch vụ Nhà phát triển hoặc Nội dung tạo sinh của Người dùng cuối;
Sự cố từ thiết bị, phần mềm, kết nối mạng, vi phạm bảo mật, tấn công mạng hoặc sự kiện bất khả kháng.
Trong phạm vi pháp luật cho phép, Nhà phát triển cam kết bồi thường, bảo vệ và giữ cho Zalo Platforms (bao gồm công ty mẹ, công ty con, bên liên kết, cán bộ nhân viên, nhà thầu, đối tác) không bị thiệt hại trước mọi khiếu nại, tranh chấp, trách nhiệm pháp lý, tiền phạt, phạt vi phạm, tổn thất, chi phí và phí luật sư hợp lý phát sinh từ hoặc liên quan đến:
Nội dung tạo sinh do Dịch vụ Nhà phát triển tạo, chỉnh sửa hoặc cung cấp (bao gồm nhưng không giới hạn ở dữ liệu, thông tin, kịch bản, câu lệnh, văn bản, hình ảnh, âm thanh, video);
Mọi tranh chấp, khiếu nại hoặc nghĩa vụ giữa Nhà phát triển và Người dùng cuối liên quan đến việc cung cấp, truy cập, sử dụng Dịch vụ Nhà phát triển hoặc phát sinh từ Nội dung tạo sinh;
Việc không cung cấp đầy đủ cảnh báo, hướng dẫn và/hoặc không kiểm chứng Nội dung tạo sinh trước khi áp dụng trong tình huống có hệ quả quan trọng.
Trong mọi trường hợp, tổng mức trách nhiệm của Zalo Platforms đối với mọi yêu cầu, khiếu nại hoặc tranh chấp liên quan đến việc sử dụng Zalo Bot sẽ không vượt quá tổng số tiền mà Nhà phát triển đã thực tế thanh toán cho Zalo Platforms trong vòng ba (03) tháng gần nhất trước thời điểm phát sinh khiếu nại, nếu có. Nếu Nhà phát triển sử dụng Zalo Bot theo hình thức miễn phí, Zalo Platforms không có bất kỳ trách nhiệm tài chính nào đối với Nhà phát triển, ngoại trừ các nghĩa vụ bắt buộc theo quy định pháp luật.
Không nội dung nào trong Điều khoản Dịch vụ này được hiểu là hạn chế hoặc loại trừ bất kỳ quyền nào của Nhà phát triển được bảo vệ theo quy định pháp luật bắt buộc. Tuy nhiên, các giới hạn trách nhiệm này sẽ được áp dụng tối đa trong phạm vi mà pháp luật cho phép.
VII. Điều Khoản Chấm Dứt
Chấm dứt bởi Nhà phát triển:
Nhà phát triển có thể chấm dứt việc sử dụng Zalo Bot bất kỳ lúc nào bằng cách:
Ngừng sử dụng, ngừng truy cập Zalo Bot;
Hủy Dịch vụ nền tảng hoặc Tài khoản Nhà phát triển theo hướng dẫn chính thức từ Zalo Platforms ;
Yêu cầu Zalo Platforms hỗ trợ chấm dứt thông qua kênh liên hệ chính thức.
Trong trường hợp chấm dứt, Nhà phát triển chịu trách nhiệm lưu trữ hoặc sao lưu dữ liệu, bao gồm dữ liệu cá nhân trước khi tài khoản bị xóa.
Chấm dứt bởi Zalo Platforms:
Zalo Platforms có thể, theo toàn quyền quyết định và không cần thông báo trước, tạm ngưng hoặc chấm dứt quyền truy cập của Nhà phát triển vào toàn bộ hoặc một phần của Zalo Bot trong các trường hợp sau:

Nhà phát triển vi phạm bất kỳ nội dung nào trong Điều khoản Dịch vụ này;
Có dấu hiệu sử dụng Zalo Bot thực hiện các hành vi bị cấm hoặc gây rủi ro cho hệ thống, dữ liệu, Người dùng cuối, Nhà phát triển khác hoặc uy tín của Zalo Platforms;
Theo yêu cầu từ cơ quan có thẩm quyền hoặc theo quy định pháp luật;
Zalo Platforms ngừng cung cấp toàn bộ hoặc một phần Dịch vụ nền tảng vì lý do kỹ thuật, thương mại hoặc chiến lược.
Hệ quả của việc chấm dứt
Khi việc chấm dứt có hiệu lực:

Nhà phát triển mất quyền truy cập vào Tài khoản Nhà phát triển và mọi Tài khoản Bot, bất kỳ dữ liệu nào liên quan trong Zalo Bot, tùy vào chính sách lưu trữ và bảo vệ dữ liệu của Zalo Platforms;
Mọi Gói dịch vụ nền tảng chưa kết thúc có thể bị hủy bỏ ngay lập tức, và Nhà phát triển không có quyền yêu cầu hoàn tiền, trừ khi có thỏa thuận khác bằng văn bản;
Zalo Platforms có thể lưu giữ hoặc xóa dữ liệu liên quan theo quy định pháp luật, chính sách bảo mật và thời gian lưu trữ nội bộ.
Việc chấm dứt theo Điều này không giới hạn quyền của Zalo Platforms trong việc yêu cầu bồi thường thiệt hại; thực hiện các biện pháp pháp lý khác theo quy định pháp luật hoặc Điều khoản Dịch vụ này hoặc xử lý các hành vi vi phạm đã xảy ra trong thời gian sử dụng trước đó.
VIII. Sử dụng hợp lệ và cấm sử dụng
Mục đích sử dụng hợp lệ
Nhà phát triển chỉ được sử dụng Zalo Bot trong phạm vi được cho phép theo Điều khoản Dịch vụ này, vì mục đích hợp pháp, cá nhân và thương mại. Việc sử dụng hợp lệ bao gồm nhưng không giới hạn ở:

Sử dụng các chức năng đã được Zalo Platforms công bố chính thức và cấp phép sử dụng;
Tuân thủ đầy đủ quy định pháp luật và không xâm phạm quyền hoặc lợi ích hợp pháp của bất kỳ cá nhân, tổ chức nào.
Các hành vi bị nghiêm cấm
Nhà phát triển không được sử dụng Zalo Bot cho bất kỳ mục đích nào trái với quy định tại Điều khoản Dịch vụ này, bao gồm nhưng không giới hạn ở:

Hành vi xâm phạm hệ thống và nền tảng:

Truy cập trái phép vào hệ thống, dữ liệu, mã nguồn, giao diện lập trình ứng dụng (API) hoặc tài nguyên nội bộ của Zalo Bot;
Phá hoại, gây quá tải, làm gián đoạn hoặc làm suy giảm hiệu năng hoặc tính ổn định của Zalo Bot;
Sử dụng công cụ tự động (bot, script, crawler...) để truy xuất, thu thập, sao chép hoặc tái tạo bất kỳ phần nào của Zalo Bot.
Hành vi lạm dụng Zalo Bot, Bot hoặc Nội dung tạo sinh:

Nhà phát triển cam kết không tạo ra, tải lên, phát tán hoặc sử dụng hệ thống phần mềm để cung cấp, tạo ra, chỉnh sửa, phát hành, trực tiếp hay gián tiếp, bất kỳ nội dung nào có một trong các dấu hiệu sau:

Vi phạm pháp luật Việt Nam hoặc điều ước quốc tế mà Việt Nam là thành viên;
Vi phạm quyền sở hữu trí tuệ, quyền riêng tư, quyền nhân thân hoặc các quyền hợp pháp khác của bất kỳ cá nhân, tổ chức hoặc bên thứ ba nào;
Chứa thông tin sai lệch, xuyên tạc, gây hiểu nhầm hoặc kích động thù địch, bạo lực, kỳ thị, phân biệt đối xử;
Trái với thuần phong mỹ tục, đạo đức xã hội hoặc các tiêu chuẩn cộng đồng hợp lý; bao gồm nhưng không giới hạn ở các nội dung khiêu dâm, đồi trụy, bạo lực cực đoan, ngôn ngữ thô tục hoặc xúc phạm tôn giáo, sắc tộc;
Xâm phạm đến trẻ em dưới bất kỳ hình thức nào, bao gồm việc gợi dục, khai thác hình ảnh, hoặc gây tổn hại về thể chất, tinh thần hoặc đạo đức cho trẻ em;
Phổ biến hoặc cổ súy cho hành vi tự sát, tự gây hại hoặc bạo lực đối với bản thân hoặc người, vật khác;
Mang tính chất gian lận, giả mạo, lừa đảo, mạo danh cơ quan/tổ chức/cá nhân, hoặc vi phạm niềm tin chính đáng của Nhà phát triển khác;
Truyền bá mã độc, phần mềm độc hại, phần mềm gián điệp, mã khai thác hệ thống hoặc bất kỳ nội dung nào có khả năng gây tổn hại đến thiết bị, dữ liệu hoặc an ninh của Zalo Bot, hệ thống Zalo Platforms hoặc bên thứ ba khác;
Cản trở, gây nhiễu, tấn công hệ thống hoặc làm ảnh hưởng đến hiệu năng, độ tin cậy hoặc tính bảo mật của Zalo Bot;
Sử dụng Nội dung tạo sinh để huấn luyện hoặc phát triển mô hình trí tuệ nhân tạo khác, sản phẩm, Dịch vụ hoặc hệ thống có tính chất cạnh tranh với Zalo Bot hoặc với sản phẩm khác của Zalo Platforms; hoặc
Vi phạm chính sách công, đạo luật chuyên ngành, hoặc các giới hạn pháp lý có liên quan đến lĩnh vực hoạt động của Nhà phát triển (ví dụ: sử dụng Output để ra quyết định trong lĩnh vực tài chính, y tế, pháp lý, giáo dục mà không có chuyên môn hợp pháp).
Hành vi vi phạm pháp luật hoặc quyền riêng tư:

Vi phạm bất kỳ quy định pháp luật hiện hành nào, bao gồm nhưng không giới hạn ở: Luật Bảo vệ dữ liệu cá nhân 2025, Luật Dữ liệu 2024, Luật An toàn thông tin mạng, Luật An ninh mạng, Luật Bảo vệ quyền lợi người tiêu dùng, Luật Trẻ em, Luật Sở hữu trí tuệ và các luật khác;
Sử dụng hệ thống phần mềm để tạo ra hoặc xử lý Dữ liệu cá nhân của Người dung cuối hoặc bên thứ ba mà không có sự đồng ý hợp pháp;
Sử dụng hệ thống phần mềm để ra quyết định tự động liên quan đến tín dụng, giáo dục, chăm sóc sức khỏe, pháp lý, hoặc các lĩnh vực chuyên môn mà không có sự xác minh của chuyên gia có thẩm quyền hoặc cảnh báo Người dùng cuối.
Các biện pháp xử lý vi phạm
Trong trường hợp phát hiện hoặc có căn cứ cho rằng Nhà phát triển vi phạm bất kỳ quy định nào trong Phần này, Zalo Platforms có quyền:

Tạm ngưng hoặc chấm dứt tài khoản hoặc quyền truy cập của Nhà phát triển mà không cần thông báo trước;
Gỡ bỏ, khóa hoặc vô hiệu hóa bất kỳ nội dung vi phạm nào;
Lưu trữ và chuyển giao thông tin vi phạm cho cơ quan có thẩm quyền theo quy định pháp luật;
Áp dụng các biện pháp pháp lý và kỹ thuật phù hợp để bảo vệ quyền lợi hợp pháp của Zalo Platforms và cộng đồng Nhà phát triển và Người dùng cuối.
IX. Điều khoản bất khả kháng
Định nghĩa sự kiện bất khả kháng
"Sự kiện bất khả kháng" là bất kỳ sự kiện xảy ra một cách khách quan mà Zalo Platforms không thể lường trước được và không thể khắc phục được mặc dù Zalo Platforms đã áp dụng mọi biện pháp cần thiết và khả năng cho phép, bao gồm nhưng không giới hạn ở:

Thiên tai, hỏa hoạn, lũ lụt, động đất, bão, dịch bệnh, hoặc các hiện tượng thiên nhiên tương tự;
Chiến tranh, bạo loạn, đình công, khủng bố, phong tỏa, biểu tình quy mô lớn;
Sự thay đổi chính sách pháp luật, cấm vận, hoặc quyết định/hành động của cơ quan nhà nước có thẩm quyền;
Sự cố kỹ thuật nghiêm trọng như mất kết nối Internet diện rộng, mất điện lưới, tấn công mạng diện rộng, lỗi hệ thống phần cứng nghiêm trọng không thể khôi phục trong thời gian hợp lý;
Sự ngừng cung cấp hoặc gián đoạn từ nhà cung cấp hạ tầng, bên thứ ba quan trọng liên quan đến việc vận hành Zalo Bot.
Miễn trừ trách nhiệm
Trong trường hợp xảy ra sự kiện bất khả kháng, Zalo Platforms không phải chịu trách nhiệm đối với việc chậm trễ, gián đoạn hoặc không thể thực hiện nghĩa vụ theo Điều khoản Dịch vụ này, trong phạm vi bị ảnh hưởng bởi sự kiện đó.

Zalo Platforms không phải bồi thường bất kỳ tổn thất, thiệt hại hoặc nghĩa vụ nào phát sinh từ hoặc liên quan đến sự kiện bất khả kháng.

Hiệu lực tiếp tục của Điều khoản
Trừ khi có quy định khác, Điều khoản Dịch vụ này vẫn giữ nguyên hiệu lực trong và sau thời gian xảy ra sự kiện bất khả kháng. Việc tạm ngưng thực hiện một phần nghĩa vụ trong thời gian bị ảnh hưởng không đồng nghĩa với việc từ bỏ toàn bộ quyền hoặc nghĩa vụ khác theo Điều khoản Dịch vụ này.

X. Luật áp dụng và biện pháp giải quyết tranh chấp
Luật áp dụng
Toàn bộ nội dung của Điều khoản Dịch vụ này, bao gồm nhưng không giới hạn ở việc hình thành, hiệu lực, giải thích, thực hiện và chấm dứt Điều khoản, sẽ được điều chỉnh và giải thích theo pháp luật Việt Nam, loại trừ bất kỳ nguyên tắc xung đột pháp luật nào có thể được áp dụng.

Các biện pháp giải quyết tranh chấp
Giải quyết khiếu nại của Nhà phát triển:
Nhà phát triển có quyền gửi khiếu nại, phản hồi hoặc yêu cầu giải thích liên quan đến việc sử dụng Zalo Bot hoặc việc thực hiện Điều khoản Dịch vụ này đến Zalo Platforms thông qua kênh liên hệ chính thức được nêu tại Phần Thông tin liên hệ. Zalo Platforms sẽ tiếp nhận, xác minh và phản hồi khiếu nại của Nhà phát triển trong thời hạn không quá 30 (ba mươi) ngày làm việc kể từ ngày nhận được thông tin khiếu nại hợp lệ.

Giải quyết tranh chấp:

Thương lượng và hòa giải: Bên có khiếu nại hoặc tranh chấp phải gửi văn bản thông báo đến bên còn lại, nêu rõ nội dung tranh chấp, yêu cầu cụ thể, căn cứ pháp lý hoặc thực tế và các tài liệu liên quan (nếu có). Các bên có trách nhiệm hợp tác thiện chí trong thời hạn tối đa 60 (sáu mươi) ngày kể từ ngày nhận được thông báo tranh chấp, để tiến hành thương lượng và/hoặc hòa giải. Trong thời gian thương lượng, các bên tiếp tục thực hiện các nghĩa vụ không bị tranh chấp theo Điều khoản Dịch vụ này.
Trọng tài: Nếu sau thời hạn nêu trên, các bên không đạt được thỏa thuận hoặc không giải quyết được tranh chấp bằng thương lượng hoặc hòa giải, thì tranh chấp sẽ được đưa ra giải quyết bằng trọng tài. Việc khởi kiện chỉ có thể được thực hiện sau khi bên khởi kiện chứng minh đã thực hiện đầy đủ nghĩa vụ thương lượng/hòa giải theo quy trình nêu trên, trừ khi có nguy cơ thiệt hại khẩn cấp cần bảo vệ khẩn cấp quyền và lợi ích hợp pháp.  mọi tranh chấp phát sinh từ hoặc liên quan đến Điều khoản Dịch vụ này sẽ được giải quyết bằng trọng tài tại Trung tâm Trọng tài Quốc tế Việt Nam (VIAC) theo Quy tắc tố tụng trọng tài của VIAC đang có hiệu lực tại thời điểm phát sinh tranh chấp.​ Thủ tục rút gọn sẽ được áp dụng nếu thuộc trường hợp có thể áp dụng thủ tục rút gọn theo Quy tắc tố tụng trọng tài của VIAC. Số lượng Trọng tài viên là 01 (một) Trọng tài viên duy nhất được chỉ định bởi VIAC theo Quy tắc tố tụng trọng tài của VIAC. Địa điểm trọng tài tại TP. Hồ Chí Minh, Việt Nam.​ Ngôn ngữ trọng tài là Tiếng Việt.​ Quy trình tố tụng trọng tài sẽ được tiến hành theo các quy định chi tiết tại Quy tắc tố tụng trọng tài của VIAC.
XI. Thay Đổi Điều Khoản
Quyền sửa đổi
Zalo Platforms có quyền sửa đổi, cập nhật hoặc bổ sung Điều khoản Dịch vụ này bất kỳ lúc nào để phù hợp với:

Thay đổi trong quy định pháp luật;
Cập nhật tính năng, Dịch vụ nền tảng hoặc mô hình hoạt động của Zalo Bot;
Điều chỉnh chính sách nội bộ hoặc theo chỉ đạo từ cơ quan có thẩm quyền.
Hình thức và thời điểm thông báo
Các sửa đổi sẽ được công bố qua một hoặc nhiều hình thức sau:

Trên website chính thức của Zalo Bot;
Trong ứng dụng hoặc giao diện tích hợp của Zalo Bot;
Qua email, thông báo đẩy hoặc các phương tiện thông tin khác mà Zalo Platforms cho là phù hợp.
Các sửa đổi sẽ có hiệu lực kể từ ngày được công bố, trừ khi Zalo Platforms nêu rõ hiệu lực khác trong thông báo.

Sự đồng ý ngầm định
Việc Nhà phát triển tiếp tục sử dụng Zalo Bot sau thời điểm Điều khoản Dịch vụ được sửa đổi có hiệu lực sẽ được hiểu là sự đồng ý rõ ràng và đầy đủ của Nhà phát triển đối với nội dung được cập nhật.
Nếu Nhà phát triển không đồng ý với các sửa đổi, vui lòng ngừng sử dụng Zalo Bot và thực hiện quy trình chấm dứt được quy định Điều khoản Dịch vụ này.
XII. Liên Hệ Hỗ Trợ
Kênh liên hệ chính thức:
Mọi phản hồi, câu hỏi, khiếu nại hoặc yêu cầu liên quan đến Điều khoản Dịch vụ này có thể được gửi đến Zalo Platforms thông qua một trong các kênh sau:

Email: cskh@zaloplatforms.com
Tài khoản Zalo chính thức: https://zalo.me/3899658094114941620
Địa chỉ thư tín: Công ty TNHH Zalo Platforms, Tầng 2, Tòa nhà Saigon Paragon, số 3 Nguyễn Lương Bằng, Phường Tân Mỹ, Thành phố Hồ Chí Minh, Việt Nam.
Thời gian phản hồi
Zalo Platforms cam kết tiếp nhận và xử lý thông tin Nhà phát triển trong thời gian hợp lý, ưu tiên các trường hợp liên quan đến:

Khiếu nại về tài khoản, thanh toán, quyền riêng tư, quyền đối với dữ liệu cá nhân;
Vi phạm nội dung hoặc hành vi bị cấm;
Báo cáo sự cố kỹ thuật nghiêm trọng.
Zalo Platforms cam kết giải quyết mọi phản hồi của Nhà phát triển trong thời gian sớm nhất nhằm đảm bảo trải nghiệm Dịch vụ tốt nhất. Nếu có bất kỳ thắc mắc hay yêu cầu bổ sung nào, vui lòng liên hệ với Chúng tôi.

XIII. Điều Khoản Chung
Điều khoản Dịch vụ này cấu thành toàn bộ thỏa thuận giữa Zalo Platforms và Nhà phát triển liên quan đến việc sử dụng Zalo Bot, và thay thế mọi thỏa thuận, cam kết hoặc trao đổi trước đó, bằng văn bản hoặc miệng, nếu có.
Nếu bất kỳ điều khoản nào bị xem là không hợp pháp, không còn hiệu lực hoặc không thể thực thi, điều đó sẽ không ảnh hưởng đến hiệu lực của các phần còn lại, trong phạm vi tối đa có thể.
Việc Zalo Platforms không thực hiện, hoặc trì hoãn thực hiện bất kỳ quyền nào theo Điều khoản Dịch vụ này sẽ không được hiểu là sự từ bỏ quyền đó, cũng như không ảnh hưởng đến việc thực hiện quyền đó trong tương lai. Việc từ bỏ bất kỳ quyền hoặc biện pháp xử lý nào theo Điều khoản Dịch vụ này chỉ có hiệu lực nếu được lập thành văn bản và do đại diện hợp pháp của Zalo Platforms ký xác nhận rõ ràng.
Trong trường hợp có sự khác biệt giữa bản tiếng Việt và bản dịch sang ngôn ngữ khác của Điều khoản Dịch vụ này, bản tiếng Việt sẽ được ưu tiên áp dụng.
Điều khoản Dịch vụ này có hiệu lực kể từ ngày được Zalo Platforms công bố chính thức và sẽ được cập nhật theo từng thời kỳ, phù hợp quy định tại Điều XI.