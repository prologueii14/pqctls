"""
連線級別的 PCAP 分析器（修正版）
將封包分組到各自的 TCP/UDP/QUIC 連線中
"""

from scapy.all import rdpcap, TCP, IP, IPv6, UDP
import json
from collections import defaultdict
from pathlib import Path

class ConnectionAnalyzer:
    def __init__(self, pcap_path):
        self.pcap_path = pcap_path
        self.connections = {}
        self.connection_packets = defaultdict(list)
        
    def _get_connection_id(self, packet):
        """
        從封包提取連線 ID（五元組）
        支援 IPv4、IPv6、TCP、UDP、QUIC
        """
        try:
            # 檢查是 IPv4 還是 IPv6
            ip_layer = None
            if IP in packet:
                ip_layer = packet[IP]
            elif IPv6 in packet:
                ip_layer = packet[IPv6]
            else:
                return None
            
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            
            # 處理 TCP
            if TCP in packet:
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport
                
                # 檢查是否是 HTTPS
                if dst_port == 443 or src_port == 443:
                    proto = 'HTTPS'
                else:
                    proto = 'TCP'
                
                endpoint_a = (src_ip, src_port)
                endpoint_b = (dst_ip, dst_port)
                
                if endpoint_a > endpoint_b:
                    endpoint_a, endpoint_b = endpoint_b, endpoint_a
                
                return (endpoint_a, endpoint_b, proto)
            
            # 處理 UDP
            elif UDP in packet:
                src_port = packet[UDP].sport
                dst_port = packet[UDP].dport
                
                # 檢查是否是 QUIC (通常 port 443)
                if dst_port == 443 or src_port == 443:
                    proto = 'QUIC'
                elif dst_port == 53 or src_port == 53:
                    proto = 'DNS'
                else:
                    proto = 'UDP'
                
                endpoint_a = (src_ip, src_port)
                endpoint_b = (dst_ip, dst_port)
                
                if endpoint_a > endpoint_b:
                    endpoint_a, endpoint_b = endpoint_b, endpoint_a
                
                return (endpoint_a, endpoint_b, proto)
            
        except (AttributeError, IndexError):
            pass
        
        return None
    
    def analyze(self):
        """分析 PCAP 並提取連線資訊"""
        print(f"\n讀取 PCAP: {self.pcap_path}")
        packets = rdpcap(self.pcap_path)
        print(f"總封包數: {len(packets)}")
        
        # 診斷：統計協議分布
        protocol_count = defaultdict(int)
        filtered_count = 0
        
        # 第一遍：分組封包到各自的連線
        print("\n分析連線...")
        for pkt in packets:
            # 診斷
            has_ip = False
            if IP in pkt:
                protocol_count['IPv4'] += 1
                has_ip = True
            if IPv6 in pkt:
                protocol_count['IPv6'] += 1
                has_ip = True
            
            if has_ip:
                if TCP in pkt:
                    protocol_count['TCP'] += 1
                elif UDP in pkt:
                    protocol_count['UDP'] += 1
            else:
                protocol_count['Non-IP'] += 1
            
            conn_id = self._get_connection_id(pkt)
            if conn_id:
                self.connection_packets[conn_id].append(pkt)
                filtered_count += 1
        
        # 顯示診斷資訊
        print(f"\n協議分布:")
        for proto, count in sorted(protocol_count.items()):
            print(f"  {proto:12}: {count:6} ({count/len(packets)*100:5.1f}%)")
        
        print(f"\n可分組的封包: {filtered_count}/{len(packets)} ({filtered_count/len(packets)*100:.1f}%)")
        print(f"識別出 {len(self.connection_packets)} 個連線")
        
        # 第二遍：統計每個連線的特徵
        connections = []
        for conn_id, pkts in self.connection_packets.items():
            if len(pkts) == 0:
                continue
            
            # 計算統計資訊
            total_bytes = sum(len(p) for p in pkts)
            packet_sizes = [len(p) for p in pkts]
            start_time = float(pkts[0].time)
            end_time = float(pkts[-1].time)
            duration = end_time - start_time
            
            # 提取端點資訊
            endpoint_a, endpoint_b, proto = conn_id
            
            conn_info = {
                'id': len(connections),
                'protocol': proto,
                'src': f"{endpoint_a[0]}:{endpoint_a[1]}",
                'dst': f"{endpoint_b[0]}:{endpoint_b[1]}",
                'packet_count': len(pkts),
                'total_bytes': total_bytes,
                'duration': round(duration, 3),
                'start_time': round(start_time, 3),
                'end_time': round(end_time, 3),
                'avg_packet_size': round(total_bytes / len(pkts), 2),
                'min_packet_size': min(packet_sizes),
                'max_packet_size': max(packet_sizes),
            }
            
            connections.append(conn_info)
        
        # 按開始時間排序
        connections.sort(key=lambda x: x['start_time'])
        
        # 重新編號
        for i, conn in enumerate(connections):
            conn['id'] = i
        
        self.connections = connections
        return connections
    
    def get_statistics(self):
        """取得整體統計資訊"""
        if not self.connections:
            return None
        
        total_packets = sum(c['packet_count'] for c in self.connections)
        total_bytes = sum(c['total_bytes'] for c in self.connections)
        
        if not self.connections:
            return None
            
        total_duration = max(c['end_time'] for c in self.connections) - min(c['start_time'] for c in self.connections)
        
        # 按協議分組
        by_protocol = defaultdict(lambda: {'count': 0, 'bytes': 0, 'packets': 0})
        for conn in self.connections:
            proto = conn['protocol']
            by_protocol[proto]['count'] += 1
            by_protocol[proto]['bytes'] += conn['total_bytes']
            by_protocol[proto]['packets'] += conn['packet_count']
        
        return {
            'total_connections': len(self.connections),
            'total_packets': total_packets,
            'total_bytes': total_bytes,
            'total_duration': round(total_duration, 3),
            'avg_packets_per_connection': round(total_packets / len(self.connections), 2),
            'avg_bytes_per_connection': round(total_bytes / len(self.connections), 2),
            'by_protocol': dict(by_protocol)
        }
    
    def save_features(self, output_path):
        """儲存特徵到 JSON 檔案"""
        stats = self.get_statistics()
        
        output = {
            'metadata': {
                'source_pcap': str(self.pcap_path),
                'analysis_type': 'connection_level',
            },
            'statistics': stats,
            'connections': self.connections
        }
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 轉換所有數值為基本類型（解決 Decimal 序列化問題）
        def convert_to_serializable(obj):
            if isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            elif isinstance(obj, (int, float, str, bool, type(None))):
                return obj
            else:
                return float(obj)
        
        output = convert_to_serializable(output)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 特徵已儲存到: {output_path}")
        return output_path
    
    def print_summary(self):
        """列印摘要資訊"""
        stats = self.get_statistics()
        
        print("\n" + "=" * 70)
        print("連線級別分析摘要")
        print("=" * 70)
        print(f"總連線數:         {stats['total_connections']}")
        print(f"總封包數:         {stats['total_packets']}")
        print(f"總流量:           {stats['total_bytes']:,} bytes ({stats['total_bytes']/1024/1024:.2f} MB)")
        print(f"總持續時間:       {stats['total_duration']:.2f} 秒")
        print(f"平均每連線封包:   {stats['avg_packets_per_connection']:.0f}")
        print(f"平均每連線流量:   {stats['avg_bytes_per_connection']:,.0f} bytes ({stats['avg_bytes_per_connection']/1024:.1f} KB)")
        
        # 按協議統計
        print(f"\n按協議統計:")
        for proto, data in stats['by_protocol'].items():
            print(f"  {proto:8} - 連線: {data['count']:3}, 封包: {data['packets']:6}, 流量: {data['bytes']/1024/1024:.2f} MB")
        
        print("=" * 70)
        
        # 列出前 10 個連線
        print("\n前 10 個連線:")
        print(f"{'ID':<5} {'協議':<8} {'封包數':<10} {'流量 (KB)':<12} {'持續時間 (s)':<15}")
        print("-" * 70)
        for conn in self.connections[:10]:
            print(f"{conn['id']:<5} {conn['protocol']:<8} {conn['packet_count']:<10} "
                  f"{conn['total_bytes']/1024:<12.1f} {conn['duration']:<15.2f}")
        
        if len(self.connections) > 10:
            print(f"... 還有 {len(self.connections) - 10} 個連線 ...")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("使用方式: python connection_analyzer.py <pcap_file>")
        print("範例: python connection_analyzer.py wireshark/normal_browsing_30s.pcap")
        return
    
    pcap_file = sys.argv[1]
    
    # 分析
    analyzer = ConnectionAnalyzer(pcap_file)
    analyzer.analyze()
    analyzer.print_summary()
    
    # 儲存
    output_file = Path(pcap_file).stem + '_connections.json'
    output_path = Path('simulate_base/features') / output_file
    analyzer.save_features(output_path)
    
    print(f"\n✅ 完成！現在可以用這個 JSON 檔案進行模擬")

if __name__ == "__main__":
    main()