import os
import json
from scapy.all import rdpcap, IP, IPv6, TCP, UDP, DNS
from datetime import datetime
from collections import Counter

class TrafficAnalyzer:
    def __init__(self, pcap_file):
        self.pcap_file = pcap_file
        self.packets = None
        self.features = {}
        
    def load_pcap(self):
        """載入 PCAP 檔案"""
        print(f"載入 PCAP: {self.pcap_file}")
        self.packets = rdpcap(self.pcap_file)
        print(f"✅ 載入 {len(self.packets)} 個封包\n")
        
    def extract_features(self):
        """提取封包特徵"""
        print("開始提取特徵...")
        
        packet_sizes = []
        intervals = []
        protocols = []
        
        prev_time = None
        
        for pkt in self.packets:
            # 封包大小
            packet_sizes.append(len(pkt))
            
            # 時間間隔
            if prev_time is not None:
                interval = float(pkt.time - prev_time)
                intervals.append(interval)
            prev_time = pkt.time
            
            # 改進的協議識別
            protocol = self._identify_protocol(pkt)
            protocols.append(protocol)
        
        # 統計
        protocol_counts = Counter(protocols)
        
        self.features = {
            'file': os.path.basename(self.pcap_file),
            'total_packets': len(self.packets),
            'packet_sizes': packet_sizes,
            'intervals': intervals,
            'protocol_distribution': dict(protocol_counts),
            'statistics': {
                'avg_packet_size': sum(packet_sizes) / len(packet_sizes) if packet_sizes else 0,
                'min_packet_size': min(packet_sizes) if packet_sizes else 0,
                'max_packet_size': max(packet_sizes) if packet_sizes else 0,
                'avg_interval': sum(intervals) / len(intervals) if intervals else 0,
                'min_interval': min(intervals) if intervals else 0,
                'max_interval': max(intervals) if intervals else 0,
            }
        }
        
        print("✅ 特徵提取完成\n")
    
    def _identify_protocol(self, pkt):
        """改進的協議識別"""
        
        # 檢查 IPv4 或 IPv6
        ip_layer = None
        if IP in pkt:
            ip_layer = pkt[IP]
        elif IPv6 in pkt:
            ip_layer = pkt[IPv6]
        
        if ip_layer is None:
            return 'Ethernet'
        
        # TCP 層
        if TCP in pkt:
            sport = pkt[TCP].sport
            dport = pkt[TCP].dport
            
            # HTTPS/TLS (port 443)
            if sport == 443 or dport == 443:
                return 'HTTPS'
            
            # HTTP (port 80)
            elif sport == 80 or dport == 80:
                return 'HTTP'
            
            # 其他常見 TCP 服務
            elif sport == 22 or dport == 22:
                return 'SSH'
            elif sport == 21 or dport == 21:
                return 'FTP'
            elif sport == 25 or dport == 25:
                return 'SMTP'
            else:
                return 'TCP'
        
        # UDP 層
        elif UDP in pkt:
            sport = pkt[UDP].sport
            dport = pkt[UDP].dport
            
            # DNS
            if DNS in pkt:
                return 'DNS'
            
            # QUIC (常用 port 443 或 80)
            elif sport == 443 or dport == 443 or sport == 80 or dport == 80:
                return 'QUIC'
            
            # 其他常見 UDP 服務
            elif sport == 53 or dport == 53:
                return 'DNS'
            elif sport == 123 or dport == 123:
                return 'NTP'
            elif sport == 5353 or dport == 5353:
                return 'mDNS'
            else:
                return 'UDP'
        
        # 其他 IP 協議
        else:
            if isinstance(ip_layer, IPv6):
                return 'IPv6'
            else:
                return 'IP'
        
    def print_summary(self):
        """顯示摘要"""
        print("=" * 60)
        print(f"檔案: {self.features['file']}")
        print("=" * 60)
        print(f"總封包數:     {self.features['total_packets']}")
        print(f"平均封包大小: {self.features['statistics']['avg_packet_size']:.2f} bytes")
        print(f"最小封包:     {self.features['statistics']['min_packet_size']} bytes")
        print(f"最大封包:     {self.features['statistics']['max_packet_size']} bytes")
        print(f"平均間隔:     {self.features['statistics']['avg_interval']:.4f} 秒")
        
        print("\n協議分布:")
        for proto, count in self.features['protocol_distribution'].items():
            percentage = (count / self.features['total_packets']) * 100
            print(f"  {proto:8s}: {count:5d} ({percentage:5.2f}%)")
        print("=" * 60 + "\n")
        
    def save_features(self, output_file):
        """儲存特徵到 JSON"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 為了減小檔案大小，只保存統計摘要
        output_data = {
            'file': self.features['file'],
            'total_packets': self.features['total_packets'],
            'protocol_distribution': self.features['protocol_distribution'],
            'statistics': self.features['statistics'],
            'packet_size_sample': self.features['packet_sizes'][:100],  # 只保存前 100 個
            'interval_sample': self.features['intervals'][:100],
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 特徵已儲存到: {output_file}\n")
        
    def analyze(self, output_dir='simulate_base/features'):
        """完整分析流程"""
        self.load_pcap()
        self.extract_features()
        self.print_summary()
        
        # 自動產生輸出檔名
        base_name = os.path.splitext(os.path.basename(self.pcap_file))[0]
        output_file = os.path.join(output_dir, f'{base_name}_features.json')
        
        self.save_features(output_file)
        
        return self.features

def main():
    """測試分析器"""
    
    # 分析 PQC-TLS 流量
    print("\n" + "🔍 分析 PQC-TLS 流量".center(60, "=") + "\n")
    pqc_analyzer = TrafficAnalyzer('simulate_base/wireshark/20251104.pcap')
    pqc_analyzer.analyze()
    
    # 分析正常瀏覽流量
    print("\n" + "🔍 分析正常瀏覽流量".center(60, "=") + "\n")
    normal_analyzer = TrafficAnalyzer('simulate_base/wireshark/normal_browsing_30s.pcap')
    normal_analyzer.analyze()
    
    print("\n✅ 所有分析完成！")
    print("特徵檔案已儲存到 simulate_base/features/\n")

if __name__ == "__main__":
    main()