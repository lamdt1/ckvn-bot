import urllib.request
import json
import os

def load_env_manually():
    """Đọc file .env thủ công để không phụ thuộc vào thư viện bên ngoài"""
    env_vars = {}
    # Thử tìm file .env ở thư mục hiện tại hoặc thư mục cha (nếu chạy từ src/)
    possible_paths = [".env", "../.env"]
    file_path = None
    for p in possible_paths:
        if os.path.exists(p):
            file_path = p
            break
            
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def get_chat_id():
    env = load_env_manually()
    token = env.get("TELEGRAM_BOT_TOKEN")
    
    if not token or token == "your_telegram_bot_token" or token.startswith("your_"):
        print("❌ Lỗi: TELEGRAM_BOT_TOKEN trong file .env chưa đúng.")
        return

    # 1. Kiểm tra Bot Info trước
    print(f"📡 Đang kiểm tra Token...")
    try:
        with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/getMe") as response:
            bot_info = json.loads(response.read().decode())
            if bot_info.get("ok"):
                res = bot_info["result"]
                bot_name = res.get("first_name")
                bot_user = res.get("username")
                print(f"✅ Đã kết nối với Bot: {bot_name} (@{bot_user})")
            else:
                print("❌ Token không hợp lệ.")
                return
    except Exception as e:
        print(f"❌ Không thể kết nối tới Telegram API: {e}")
        return

    # 2. Lấy Chat ID
    print(f"🔍 Đang tìm kiếm tin nhắn mới để lấy Chat ID...")
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        results = data.get("result", [])
        if not results:
            print("\n" + "!"*40)
            print("⚠️ KHÔNG TÌM THẤY TIN NHẮN!")
            print("!"*40)
            print(f"Để script lấy được ID, bạn hãy:")
            print(f"1. Mở Telegram, tìm bot: @{bot_user}")
            print(f"2. Gửi một tin nhắn bất kỳ (ví dụ: gõ 'hello')")
            print(f"3. CHẠY LẠI script này ngay lập tức.")
            print("!"*40)
            return

        found = False
        for item in reversed(results):
            chat_info = None
            user_info = None
            
            if "message" in item:
                chat_info = item["message"]["chat"]
                user_info = item["message"]["from"]
            elif "my_chat_member" in item:
                chat_info = item["my_chat_member"]["chat"]
                user_info = item["my_chat_member"]["from"]
            elif "callback_query" in item:
                chat_info = item["callback_query"]["message"]["chat"]
                user_info = item["callback_query"]["from"]

            if chat_info:
                chat_id = chat_info["id"]
                chat_type = chat_info.get("type", "unknown")
                username = user_info.get("username", "n/a")
                first_name = user_info.get("first_name", "User")
                
                print("\n" + "="*40)
                print(f"🎉 THÀNH CÔNG! ĐÃ TÌM THẤY CHAT ID")
                print("="*40)
                print(f"🆔 Chat ID: {chat_id}")
                print(f"👤 Từ User: {first_name} (@{username})")
                print(f"📁 Loại: {chat_type}")
                print("="*40)
                print(f"\n👉 Hãy copy dãy số {chat_id} (bao gồm cả dấu trừ nếu có)")
                print(f"👉 Dán vào file .env tại dòng: TELEGRAM_CHAT_ID={chat_id}")
                found = True
                break
        
        if not found:
            print("❌ Dữ liệu trả về không chứa thông tin Chat ID.")
            
    except Exception as e:
        print(f"❌ Lỗi khi lấy ID: {e}")

if __name__ == "__main__":
    get_chat_id()
