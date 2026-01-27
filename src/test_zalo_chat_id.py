import httpx
import time

BOT_TOKEN = "738499441022218443:HcapvQPPTFJvrEXqZKzNvJQwkrXeYJAtUTbWIXoJzYqVzHNwFctDVCBpkEoPWTbL"
url = f"https://bot-api.zaloplatforms.com/bot{BOT_TOKEN}/getUpdates"

print("🚀 Đang chờ tin nhắn từ Zalo... (Hãy nhắn tin cho Bot của bạn)")

while True:
    try:
        response = httpx.post(url, json={"timeout": 30}, timeout=40.0)
        data = response.json()

        if data.get("ok"):
            if data.get("result"):
                # Duyệt qua các update
                result = data["result"]
                message = result.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                
                if chat_id:
                    print(f"\n✅ Tìm thấy! ZALO_CHAT_ID của bạn: {chat_id}")
                    break
            else:
                # Không có tin nhắn mới trong 30s qua
                print(".", end="", flush=True)
        else:
            # Zalo API trả về lỗi (bao gồm 408 Request Timeout)
            if "Request timeout" in str(data.get("description")):
                print(".", end="", flush=True)
            else:
                print(f"\n❌ Lỗi API: {data.get('description')}")
                # Nếu token lỗi thì dừng, nếu lỗi khác thì chờ rồi tiếp tục
                if data.get("error_code") == 401:
                    break
                
    except httpx.ReadTimeout:
        # Httpx timeout, tiếp tục loop
        print(".", end="", flush=True)
    except Exception as e:
        print(f"\n❌ Lỗi socket/mạng: {e}")
        time.sleep(5)

    time.sleep(1)