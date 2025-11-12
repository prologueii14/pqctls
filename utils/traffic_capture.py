import os
from scapy.all import wrpcap, TCP, conf, AsyncSniffer
from datetime import datetime
from utils.settings import settings
import threading

class TrafficCapture:
    def __init__(self, port=8443, output_dir='data/pcaps', interface=None):
        self.port = port
        self.output_dir = output_dir
        self.interface = interface
        os.makedirs(output_dir, exist_ok=True)
        
        self.packets = []
        self.is_capturing = False
        self.capture_thread = None
        self.sniffer = None  # AsyncSniffer 實例

        # 使用預設網卡捕獲（不強制 loopback）
        # BPF 過濾器會確保只捕獲指定 port 的流量
        # if not self.interface:
        #     self.interface = self._find_loopback_interface()
    
    def _find_loopback_interface(self):
        """尋找 loopback 介面"""
        try:
            # Windows 上 Npcap 的 loopback 介面名稱
            for iface_name in conf.ifaces:
                iface = conf.ifaces[iface_name]
                # 尋找包含 "Loopback" 或 "127.0.0.1" 的介面
                if 'Loopback' in iface.description or 'Loopback' in iface_name:
                    print(f"[OK] 找到 Loopback 介面: {iface.description}")
                    return iface_name

            # 如果找不到，返回 None（使用預設）
            print("[WARN] 未找到 Loopback 介面，使用預設介面")
            return None
        except Exception as e:
            print(f"[WARN] 搜尋介面時出錯: {e}")
            return None
    
    def start(self, count=0, timeout=None):
        """
        開始捕獲流量（使用 AsyncSniffer 進行背景捕獲）

        Args:
            count: 捕獲封包數量（0=無限制）
            timeout: 超時時間（秒）
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_file = os.path.join(self.output_dir, f'capture_{timestamp}.pcap')

        print("=" * 60)
        print("[CAPTURE] 開始捕獲流量")
        print("=" * 60)
        print(f"Port:          {self.port}")
        if self.interface:
            print(f"介面:          {self.interface}")
        print(f"輸出檔案:      {self.output_file}")
        print(f"封包數量限制:  {count if count > 0 else '無限制'}")
        if timeout:
            print(f"超時:          {timeout} 秒")
        print("=" * 60)
        print("\n開始監聽...\n")

        self.is_capturing = True

        try:
            # 使用 AsyncSniffer 進行背景捕獲
            kwargs = {
                'filter': f'tcp port {self.port}',
                'prn': self._packet_callback,
                'store': True  # 儲存封包
            }

            if self.interface:
                kwargs['iface'] = self.interface
            if count > 0:
                kwargs['count'] = count

            # 啟動非同步捕獲器
            self.sniffer = AsyncSniffer(**kwargs)
            self.sniffer.start()

            # 如果有 timeout，等待指定時間後停止
            if timeout:
                import time
                time.sleep(timeout)
                self.stop()
            else:
                # 無限期捕獲，等待外部調用 stop()
                pass

        except Exception as e:
            print(f"\n[ERROR] 捕獲錯誤: {e}")
            import traceback
            traceback.print_exc()
            self.is_capturing = False
    
    def start_background(self):
        """在背景執行緒中開始捕獲"""
        if self.capture_thread and self.capture_thread.is_alive():
            print("[WARN] 已有捕獲執行緒在運行")
            return

        self.capture_thread = threading.Thread(target=self.start, daemon=True)
        self.capture_thread.start()
        print("[OK] 背景流量捕獲已啟動")
    
    def stop(self):
        """停止捕獲"""
        if not self.is_capturing:
            return

        self.is_capturing = False

        # 停止 AsyncSniffer
        if self.sniffer:
            print("\n停止捕獲器...")
            try:
                # 檢查 sniffer 是否正在運行
                if hasattr(self.sniffer, 'running') and self.sniffer.running:
                    self.sniffer.stop()

                # 取得捕獲的封包
                if hasattr(self.sniffer, 'results'):
                    self.packets = self.sniffer.results
                else:
                    self.packets = []

            except Exception as e:
                print(f"[WARN] 停止捕獲時發生錯誤: {e}")
                self.packets = []

            # 儲存封包
            if self.packets:
                self._save_packets()
            else:
                print("[WARN] 未捕獲到任何封包")
    
    def _packet_callback(self, packet):
        """封包回調，即時顯示資訊"""
        if TCP in packet:
            flags = packet[TCP].flags
            flag_str = str(flags)  # 轉成字串避免 FlagValue 格式化錯誤
            src = f"{packet[0][1].src}:{packet[TCP].sport}"
            dst = f"{packet[0][1].dst}:{packet[TCP].dport}"
            length = len(packet)

            print(f"[{len(self.packets)+1:4d}] {src:21} → {dst:21} | Flags: {flag_str:>4} | Len: {length:5d}")
    
    def _save_packets(self):
        """儲存封包到 pcap 檔案"""
        if not self.packets:
            print("\n[WARN] 沒有捕獲到封包")
            return

        wrpcap(self.output_file, self.packets)
        print(f"\n{'=' * 60}")
        print(f"[OK] 已儲存 {len(self.packets)} 個封包到:")
        print(f"   {self.output_file}")
        print(f"{'=' * 60}")
        
        self._print_statistics()
    
    def _print_statistics(self):
        """顯示統計資訊"""
        if not self.packets:
            return
        
        total_bytes = sum(len(pkt) for pkt in self.packets)
        tcp_packets = sum(1 for pkt in self.packets if TCP in pkt)
        
        print(f"\n統計資訊:")
        print(f"  總封包數:     {len(self.packets)}")
        print(f"  TCP 封包:     {tcp_packets}")
        print(f"  總流量:       {total_bytes:,} bytes ({total_bytes/1024:.2f} KB)")
        
        # TLS 握手封包（通常在連線建立初期）
        if len(self.packets) >= 20:
            tls_handshake_size = sum(len(pkt) for pkt in self.packets[:20] if TCP in pkt)
            print(f"  握手階段流量: ~{tls_handshake_size:,} bytes ({tls_handshake_size/1024:.2f} KB)")

if __name__ == "__main__":
    # 測試：列出所有可用介面
    print("可用的網路介面:")
    for iface_name in conf.ifaces:
        iface = conf.ifaces[iface_name]
        print(f"  - {iface_name}: {iface.description}")
    
    print("\n" + "=" * 60)
    
    # 可以直接執行此檔案測試捕獲
    capture = TrafficCapture(port=8443)
    capture.start(timeout=30)