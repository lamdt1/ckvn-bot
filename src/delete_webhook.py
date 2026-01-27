# delete_webhook.py
import httpx

BOT_TOKEN = "738499441022218443:HcapvQPPTFJvrEXqZKzNvJQwkrXeYJAtUTbWIXoJzYqVzHNwFctDVCBpkEoPWTbL"
url = f"https://bot-api.zaloplatforms.com/bot{BOT_TOKEN}/deleteWebhook"

print("🔄 Đang xóa Webhook...")
response = httpx.post(url, json={})
data = response.json()

if data.get("ok"):
    print("✅ Xóa Webhook thành công!")
    print(f"📊 Kết quả: {data.get('result')}")
    print("\n💡 Bây giờ bạn có thể chạy lại test_zalo_chat_id.py")
else:
    print(f"❌ Lỗi: {data.get('description')}")
