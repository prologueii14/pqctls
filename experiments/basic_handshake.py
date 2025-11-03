import time
import threading
from core.normal_server import TLSServer
from core.normal_client import TLSClient
from utils.traffic_capture import TrafficCapture

# 使用不同的 port
TEST_PORT = 8443  # 改用 8443

def run_server():
    """執行 Server"""
    server = TLSServer(port=TEST_PORT)
    server.start()

def run_client():
    """執行 Client"""
    time.sleep(3)  # 等待 Server 啟動
    
    client = TLSClient(port=TEST_PORT)
    client.connect(message="GET / HTTP/1.0")
    
    print("\n等待 5 秒讓捕獲完成...")
    time.sleep(5)

def main():
    print("=" * 60)
    print(f"PQC-TLS 基本握手測試 (Port: {TEST_PORT})")
    print("=" * 60)
    
    # 1. 啟動 Server（背景執行緒）
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    print("\n等待 Server 啟動...\n")
    time.sleep(2)
    
    # 2. 啟動流量捕獲（背景執行緒）
    capture = TrafficCapture(port=TEST_PORT)
    capture_thread = threading.Thread(
        target=lambda: capture.start(timeout=20),
        daemon=True
    )
    capture_thread.start()
    
    time.sleep(2)
    
    # 3. 執行 Client
    run_client()
    
    # 4. 等待捕獲完成
    capture_thread.join()
    
    print("\n✅ 測試完成！")
    print("可以查看 data/pcaps/ 目錄下的 pcap 檔案")

if __name__ == "__main__":
    main()