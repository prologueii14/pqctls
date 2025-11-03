"""
流量模擬器 - 基於連線的重放版本
"""

import time
import threading
from pathlib import Path
from simulate_base.simulation_client import SimulationClient
from simulate_base.simulation_server import SimulationServer
from simulate_base.source_manager import SourceManager

class TrafficSimulator:
    def __init__(self, config_path='simulate_base/simulation_config.yaml'):
        self.config_path = config_path
        self.source_manager = SourceManager(config_path)
        self.features = None
        self.server = None
        self.server_port = 8443
        
        self.stats = {
            'total_connections': 0,
            'successful_connections': 0,
            'failed_connections': 0,
            'total_bytes': 0,
            'start_time': 0,
            'end_time': 0
        }
    
    def setup(self):
        """設置模擬環境"""
        print("\n" + "=" * 70)
        print("設置流量模擬器")
        print("=" * 70)
        
        # 載入配置
        config = self.source_manager.get_config()
        self.server_port = config.get('topology', {}).get('port', 8443)
        
        # 載入特徵
        self.features = self.source_manager.get_features()
        
        # 檢查是否有連線資訊
        if 'connections' not in self.features:
            print("\n❌ 錯誤: 特徵檔案缺少連線資訊")
            print("當前檔案格式為舊的封包級別格式。")
            print("\n請使用 connection_analyzer.py 重新分析 PCAP:")
            print("  python simulate_base/connection_analyzer.py simulate_base/wireshark/xxx.pcap")
            print("\n然後更新 simulation_config.yaml 中的 sources.path 為:")
            print("  path: 'features/xxx_connections.json'")
            return False
        
        connections = self.features['connections']
        stats = self.features.get('statistics', {})
        
        print(f"✅ 載入 {len(connections)} 個連線")
        print(f"   總流量: {stats.get('total_bytes', 0):,} bytes ({stats.get('total_bytes', 0)/1024/1024:.2f} MB)")
        print(f"   持續時間: {stats.get('total_duration', 0):.2f} 秒")
        
        # 啟動 Server
        print(f"\n啟動 Server (port: {self.server_port})...")
        self.server = SimulationServer(port=self.server_port)
        
        # 背景執行
        server_thread = threading.Thread(
            target=self.server.start,
            daemon=True
        )
        server_thread.start()
        
        time.sleep(3)
        
        # 測試連線
        print("測試 Server 連線...")
        test_client = SimulationClient(port=self.server_port, silent=True)
        
        try:
            if test_client.connect(message="test"):
                print("✅ Server 已就緒\n")
                return True
            else:
                print("❌ Server 測試連線失敗")
                return False
        except Exception as e:
            print(f"❌ Server 連線錯誤: {e}")
            return False
    
    def run(self):
        """執行模擬"""
        if not self.features:
            print("❌ 請先執行 setup()")
            return
        
        config = self.source_manager.get_config()
        mode = config.get('simulation', {}).get('mode', 'replay')
        
        print(f"執行模式: {mode}")
        
        if mode == 'replay':
            self._run_replay()
        else:
            print("⚠️  statistical 模式尚未實作，使用 replay 模式")
            self._run_replay()
    
    def _run_replay(self):
        """基於連線的重放模擬"""
        connections = self.features['connections']
        stats = self.features.get('statistics', {})
        
        print("\n開始連線級別重放...")
        print("=" * 70)
        print(f"來源連線數:   {len(connections)}")
        print(f"來源總流量:   {stats.get('total_bytes', 0):,} bytes ({stats.get('total_bytes', 0)/1024/1024:.2f} MB)")
        print(f"來源持續時間: {stats.get('total_duration', 0):.2f} 秒")
        
        # 顯示協議分布
        if 'by_protocol' in stats:
            print(f"\n來源協議分布:")
            for proto, data in stats['by_protocol'].items():
                print(f"  {proto:8} - {data['count']:3} 連線, {data['packets']:6} 封包, {data['bytes']/1024/1024:6.2f} MB")
        
        print("=" * 70)
        
        # 建立 Client
        client = SimulationClient(port=self.server_port, silent=True)
        self.stats['start_time'] = time.time()
        
        print("\n開始模擬...\n")
        
        # 模擬每個連線
        for i, conn in enumerate(connections):
            size = conn['total_bytes']
            protocol = conn['protocol']
            
            # 建立連線（簡化：用假資料）
            # 每次 TLS 連線會自動產生多個封包
            message = "X" * min(size, 1000)
            
            try:
                result = client.connect(message=message)
                
                if result:
                    self.stats['successful_connections'] += 1
                    self.stats['total_bytes'] += size
                else:
                    self.stats['failed_connections'] += 1
            except Exception as e:
                self.stats['failed_connections'] += 1
                if i < 5:  # 只顯示前 5 個錯誤
                    print(f"  ⚠️  連線 {i+1} 失敗: {e}")
            
            self.stats['total_connections'] += 1
            
            # 進度顯示
            if (i + 1) % 10 == 0 or (i + 1) == len(connections):
                progress = (i + 1) / len(connections) * 100
                elapsed = time.time() - self.stats['start_time']
                rate = self.stats['total_connections'] / elapsed if elapsed > 0 else 0
                
                print(f"進度: {i + 1:4}/{len(connections):4} ({progress:5.1f}%) | "
                      f"成功: {self.stats['successful_connections']:4} | "
                      f"失敗: {self.stats['failed_connections']:3} | "
                      f"耗時: {elapsed:6.1f}s | "
                      f"速率: {rate:5.1f} conn/s")
            
            # 連線間隔（加速 10 倍，且限制最大間隔）
            if i < len(connections) - 1:
                next_conn = connections[i + 1]
                interval = next_conn['start_time'] - conn['end_time']
                if interval > 0:
                    time.sleep(min(interval / 10, 0.1))
        
        self.stats['end_time'] = time.time()
        
        print("\n" + "=" * 70)
        self._print_summary()
    
    def _print_summary(self):
        """列印摘要"""
        duration = self.stats['end_time'] - self.stats['start_time']
        success_rate = (self.stats['successful_connections'] / self.stats['total_connections'] * 100) if self.stats['total_connections'] > 0 else 0
        
        print("模擬完成摘要")
        print("=" * 70)
        print(f"總連線數:     {self.stats['total_connections']}")
        print(f"成功連線:     {self.stats['successful_connections']} ({success_rate:.1f}%)")
        print(f"失敗連線:     {self.stats['failed_connections']}")
        print(f"模擬流量:     {self.stats['total_bytes']:,} bytes ({self.stats['total_bytes']/1024/1024:.2f} MB)")
        print(f"執行時間:     {duration:.2f} 秒 ({duration/60:.1f} 分鐘)")
        
        if duration > 0:
            throughput = self.stats['total_bytes'] / duration / 1024 / 1024
            conn_rate = self.stats['total_connections'] / duration
            print(f"平均吞吐量:   {throughput:.2f} MB/s")
            print(f"連線速率:     {conn_rate:.2f} conn/s")
        
        print("=" * 70)
    
    def stop(self):
        """停止模擬"""
        if self.server:
            print("\n停止 Server...")
            self.server.stop()
            print("✅ Server 已停止")

# 主函數
def main():
    simulator = TrafficSimulator()
    
    try:
        # 設置
        if not simulator.setup():
            print("\n❌ 設置失敗")
            return
        
        # 執行
        simulator.run()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  收到中斷信號")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理
        simulator.stop()

if __name__ == "__main__":
    main()