import time
import threading
from core.normal_server import TLSServer
from core.normal_client import TLSClient
from utils.traffic_capture import TrafficCapture

def main():
    # 1. 啟動 Server（帶 keylog）
    server = TLSServer(port=8443)
    server_thread = threading.Thread(
        target=lambda: server.start(keylog_file='data/keys/server.log'),
        daemon=True
    )
    server_thread.start()
    time.sleep(2)
    
    # 2. 啟動捕獲
    capture = TrafficCapture(port=8443)
    capture_thread = threading.Thread(
        target=lambda: capture.start(timeout=15),
        daemon=True
    )
    capture_thread.start()
    time.sleep(1)
    
    # 3. Client 連線（帶 keylog）
    client = TLSClient(port=8443)
    client.connect(
        message="GET / HTTP/1.0",
        keylog_file='data/keys/client.log'
    )
    
    time.sleep(5)
    capture_thread.join()
    
    print("\n✅ 測試完成！")
    print("現在可以用 Wireshark 開啟 PCAP 並用 keylog 解密")

if __name__ == "__main__":
    main()