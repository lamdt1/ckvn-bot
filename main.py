import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from src.config import settings
from src.portfolio import get_portfolio_manager
from src.data_loader import DataLoader
from src.engines import AnalysisEngine
from src.notifier import get_notifier
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            "status": "healthy",
            "bot_name": "Vietnam Stock Alert Bot",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def log_message(self, format, *args):
        # Override to suppress standard logging of every request
        return

def start_health_check_server():
    server_address = ('', settings.PORT)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(f"📡 Health check server đang chạy tại port {settings.PORT}")
    httpd.serve_forever()

# Khởi tạo các thành phần
portfolio_mgr = get_portfolio_manager()
notifier = get_notifier()

def is_trading_time():
    """Kiểm tra xem hiện tại có phải giờ giao dịch (Thứ 2-6, 9:00-11:30, 13:00-15:00)."""
    now = datetime.now()
    if now.weekday() > 4:  # Thứ 7 & CN
        return False
    
    current_time = now.time()
    morning_start = datetime.strptime("09:00", "%H:%M").time()
    morning_end = datetime.strptime("11:30", "%H:%M").time()
    afternoon_start = datetime.strptime("13:00", "%H:%M").time()
    afternoon_end = datetime.strptime("15:00", "%H:%M").time()

    return (morning_start <= current_time <= morning_end) or \
           (afternoon_start <= current_time <= afternoon_end)

def job():
    if not is_trading_time():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Ngoài giờ giao dịch. Đang chờ...")
        return

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Đang bắt đầu chu kỳ kiểm tra...")
    
    portfolio_data = portfolio_mgr.load_portfolio()
    if not portfolio_data:
        print("Danh mục trống. Vui lòng cập nhật portfolio.json")
        return

    symbols = list(portfolio_data.keys())
    
    # 1. Lấy giá Real-time cho toàn bộ danh mục
    df_prices = DataLoader.get_realtime_prices(symbols)
    
    for symbol, position in portfolio_data.items():
        try:
            # Tìm giá hiện tại cho mã này
            # Lưu ý: Tên cột trong vnstock có thể khác nhau tùy thời điểm, 
            # chúng ta giả định cột 'Mã CP' và 'Giá Khớp Lệnh' như code cũ.
            stock_info = df_prices[df_prices['Mã CP'] == symbol]
            if stock_info.empty:
                continue
                
            current_price = float(stock_info.iloc[0]['Giá Khớp Lệnh'])
            
            # 2. Lấy dữ liệu lịch sử để phân tích kỹ thuật
            history_df = DataLoader.get_historical_data(symbol)
            
            # 3. Phân tích tín hiệu
            signal, rsi, ma20, pnl = AnalysisEngine.analyze_signal(
                symbol, current_price, position.avg_price, history_df
            )
            
            # 4. Gửi thông báo nếu có tín hiệu
            if signal:
                # Tránh spam: Kiểm tra xem đã báo tín hiệu này chưa (ví dụ trong vòng 1 giờ qua)
                # Để đơn giản, ở ver 1 này ta cứ báo nếu có tín hiệu.
                msg = notifier.format_alert_message(symbol, signal, current_price, pnl, rsi, ma20)
                notifier.send_message(msg)
                print(f"--- Đã gửi cảnh báo cho {symbol} ({signal}) ---")
                
        except Exception as e:
            print(f"Lỗi khi xử lý mã {symbol}: {e}")

if __name__ == "__main__":
    print("🚀 Vietnam Stock Alert Bot đã khởi động!")
    print(f"Tần suất: {settings.CHECK_INTERVAL_SECONDS} giây/lần.")
    
    # Chạy Health Check Server trong thread riêng
    health_thread = threading.Thread(target=start_health_check_server, daemon=True)
    health_thread.start()
    
    scheduler = BlockingScheduler()
    # Chạy lần đầu tiên ngay lập tức
    job()
    
    # Lập lịch chạy định kỳ
    scheduler.add_job(job, 'interval', seconds=settings.CHECK_INTERVAL_SECONDS)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("👋 Bot đã dừng.")