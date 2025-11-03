import os
from scapy.all import sniff, wrpcap, TCP, conf
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
        
        # 嘗試找到 loopback 介面
        if not self.interface:
            self.interface = self._find_loopback_interface()
    
    def _find_loopback_interface(self):
        """尋找 loopback 介面"""
        try:
            # Windows 上 Npcap 的 loopback 介面名稱
            for iface_name in conf.ifaces:
                iface = conf.ifaces[iface_name]
                # 尋找包含 "Loopback" 或 "127.0.0.1" 的介面
                if 'Loopback' in iface.description or 'Loopback' in iface_name:
                    print(f"✅ 找到 Loopback 介面: {iface.description}")
                    return iface_name
            
            # 如果找不到，返回 None（使用預設）
            print("⚠️  未找到 Loopback 介面，使用預設介面")
            return None
        except Exception as e:
            print(f"⚠️  搜尋介面時出錯: {e}")
            return None
    
    def start(self, count=0, timeout=None):
        """
        開始捕獲流量
        
        Args:
            count: 捕獲封包數量（0=無限制）
            timeout: 超時時間（秒）
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_file = os.path.join(self.output_dir, f'capture_{timestamp}.pcap')
        
        print("=" * 60)
        print("📡 開始捕獲流量")
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
            # 如果有指定介面，使用它
            kwargs = {
                'filter': f'tcp port {self.port}',
                'count': count,
                'timeout': timeout,
                'prn': self._packet_callback
            }
            
            if self.interface:
                kwargs['iface'] = self.interface
            
            self.packets = sniff(**kwargs)
            
            self._save_packets()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  收到中斷信號")
            self._save_packets()
        except Exception as e:
            print(f"\n❌ 捕獲錯誤: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_capturing = False
    
    def start_background(self):
        """在背景執行緒中開始捕獲"""
        if self.capture_thread and self.capture_thread.is_alive():
            print("⚠️  已有捕獲執行緒在運行")
            return
        
        self.capture_thread = threading.Thread(target=self.start, daemon=True)
        self.capture_thread.start()
        print("✅ 背景流量捕獲已啟動")
    
    def stop(self):
        """停止捕獲"""
        self.is_capturing = False
        if self.packets:
            self._save_packets()
    
    def _packet_callback(self, packet):
        """封包回調，即時顯示資訊"""
        if TCP in packet:
            flags = packet[TCP].flags
            src = f"{packet[0][1].src}:{packet[TCP].sport}"
            dst = f"{packet[0][1].dst}:{packet[TCP].dport}"
            length = len(packet)
            
            print(f"[{len(self.packets)+1:4d}] {src:21} → {dst:21} | Flags: {flags:4} | Len: {length:5d}")
    
    def _save_packets(self):
        """儲存封包到 pcap 檔案"""
        if not self.packets:
            print("\n⚠️  沒有捕獲到封包")
            return
        
        wrpcap(self.output_file, self.packets)
        print(f"\n{'=' * 60}")
        print(f"✅ 已儲存 {len(self.packets)} 個封包到:")
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