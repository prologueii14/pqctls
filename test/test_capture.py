from utils.traffic_capture import TrafficCapture
import subprocess
import time
import threading

def generate_traffic():
    """生成一些測試流量"""
    time.sleep(2)
    print("\n生成測試流量（ping localhost）...\n")
    subprocess.run(['ping', 'localhost', '-n', '5'], capture_output=True)

print("測試 Scapy 捕獲功能...\n")

# 啟動流量生成
traffic_thread = threading.Thread(target=generate_traffic, daemon=True)
traffic_thread.start()

# 捕獲任意流量（不限制 port）
print("開始捕獲所有流量 10 秒...\n")
from scapy.all import sniff

packets = sniff(timeout=10, count=20)
print(f"\n捕獲到 {len(packets)} 個封包")

if len(packets) == 0:
    print("❌ 無法捕獲封包，可能需要管理員權限")
else:
    print("✅ Scapy 可以正常捕獲")