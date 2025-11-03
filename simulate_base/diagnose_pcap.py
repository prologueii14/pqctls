"""
PCAP 診斷工具
用於檢查 PCAP 檔案的實際內容和協議分布
"""

from scapy.all import rdpcap, Ether, IP, IPv6, TCP, UDP, ICMP, ARP, DNS
from collections import Counter
import sys

def diagnose_pcap(pcap_file):
    """診斷 PCAP 檔案"""
    print(f"\n{'='*70}")
    print(f"PCAP 診斷: {pcap_file}")
    print(f"{'='*70}\n")
    
    # 讀取封包
    print("讀取封包...")
    packets = rdpcap(pcap_file)
    print(f"✅ 總共 {len(packets)} 個封包\n")
    
    # 統計協議層
    layer_stats = Counter()
    protocol_stats = Counter()
    
    for pkt in packets:
        # 統計每個封包包含哪些層
        layers = []
        
        # Layer 2
        if Ether in pkt:
            layers.append('Ethernet')
        
        # Layer 3
        if IP in pkt:
            layers.append('IPv4')
        elif IPv6 in pkt:
            layers.append('IPv6')
        elif ARP in pkt:
            layers.append('ARP')
        
        # Layer 4+
        if TCP in pkt:
            layers.append('TCP')
            # 檢查應用層
            if pkt[TCP].dport == 443 or pkt[TCP].sport == 443:
                layers.append('HTTPS')
            elif pkt[TCP].dport == 80 or pkt[TCP].sport == 80:
                layers.append('HTTP')
        elif UDP in pkt:
            layers.append('UDP')
            # 檢查應用層
            if pkt[UDP].dport == 53 or pkt[UDP].sport == 53:
                layers.append('DNS')
            elif pkt[UDP].dport == 443 or pkt[UDP].sport == 443:
                layers.append('QUIC')
        elif ICMP in pkt:
            layers.append('ICMP')
        
        # 記錄
        for layer in layers:
            layer_stats[layer] += 1
        
        # 記錄協議組合
        protocol = ' > '.join(layers) if layers else 'Unknown'
        protocol_stats[protocol] += 1
    
    # 顯示層次統計
    print("協議層統計:")
    print(f"{'協議':<20} {'數量':>8} {'百分比':>10}")
    print("-" * 40)
    for layer, count in layer_stats.most_common():
        pct = count / len(packets) * 100
        print(f"{layer:<20} {count:>8} {pct:>9.1f}%")
    
    # 顯示協議組合（前 15 種）
    print(f"\n最常見的協議組合（前 15）:")
    print(f"{'協議組合':<40} {'數量':>8} {'百分比':>10}")
    print("-" * 60)
    for proto, count in protocol_stats.most_common(15):
        pct = count / len(packets) * 100
        print(f"{proto:<40} {count:>8} {pct:>9.1f}%")
    
    # 顯示前 10 個封包的詳細資訊
    print(f"\n前 10 個封包詳情:")
    print("-" * 70)
    for i, pkt in enumerate(packets[:10]):
        print(f"\n封包 #{i+1}:")
        print(f"  長度: {len(pkt)} bytes")
        print(f"  摘要: {pkt.summary()}")
        print(f"  包含的層: {[layer.name for layer in pkt.layers()]}")
    
    # 檢查是否有奇怪的封裝
    print(f"\n\n檢查封包封裝...")
    sample_pkt = packets[0]
    print(f"第一個封包的層次結構:")
    print(sample_pkt.show(dump=True))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方式: python diagnose_pcap.py <pcap_file>")
        print("範例: python diagnose_pcap.py wireshark/normal_browsing_30s.pcap")
        sys.exit(1)
    
    diagnose_pcap(sys.argv[1])