"""
流量模擬引擎

根據來源特徵，調度 Client-Server 連線以模擬流量
"""

import time
import random
from source_manager import SourceManager
from simulation_client import SimulationClient
from simulation_server import SimulationServer
import threading


class TrafficSimulator:
    """流量模擬引擎"""
    
    def __init__(self, config_path='simulate_base/simulation_config.yaml'):
        """
        初始化
        
        Args:
            config_path: 配置檔路徑
        """
        self.source_mgr = SourceManager(config_path)
        self.features = None
        self.config = self.source_mgr.config
        
        # 模擬模式
        self.mode = self.config['simulation']['mode']
        
        # 拓樸配置（用於 statistical 模式）
        self.num_clients = self.config['topology']['clients']
        self.server_port = self.config['topology']['server_port']
        self.connections_per_client = self.config['topology']['per_client']['connections']
        self.interval_range = self.config['topology']['per_client']['interval_range']
        
        # Statistical 模式配置
        self.duration = self.config['simulation']['duration']
        self.use_threading = self.config['simulation']['execution']['threading']
        self.max_workers = self.config['simulation']['execution']['max_workers']
        
        # Replay 模式配置
        self.replay_config = self.config['simulation'].get('replay', {})
        self.max_packets = self.replay_config.get('max_packets', 0)
        self.time_scale = self.replay_config.get('time_scale', 1.0)
        self.skip_small = self.replay_config.get('skip_small_packets', False)
        
        # Server
        self.server = None
        
        # 統計
        self.stats = {
            'total_connections': 0,
            'successful_connections': 0,
            'failed_connections': 0,
            'total_bytes': 0,
            'start_time': None,
            'end_time': None
        }
    
    def setup(self):
        """初始化設定"""
        print("\n" + "=" * 60)
        print("🚀 流量模擬器初始化")
        print("=" * 60)
        
        # 載入特徵
        self.features = self.source_mgr.get_features()
        summary = self.source_mgr.get_summary()
        
        print(f"來源封包數:   {summary['total_packets']}")
        print(f"平均封包大小: {summary['avg_packet_size']:.2f} bytes")
        print(f"平均間隔:     {summary['avg_interval']:.4f} 秒")
        
        print(f"\n模擬模式:     {self.mode.upper()}")
        
        if self.mode == 'replay':
            max_display = self.max_packets if self.max_packets > 0 else len(self.features['packet_sizes'])
            print(f"  重放封包數:   {max_display}")
            print(f"  時間縮放:     {self.time_scale}x")
            print(f"  跳過小封包:   {'是' if self.skip_small else '否'}")
        else:
            print(f"  Client 數量:  {self.num_clients}")
            print(f"  每 Client 連線: {self.connections_per_client}")
            print(f"  總連線數:     {self.num_clients * self.connections_per_client}")
            print(f"  多執行緒:     {'啟用' if self.use_threading else '禁用'}")
        
        # 啟動 Server
        print(f"\n啟動 Server (Port: {self.server_port})...")
        self.server = SimulationServer(port=self.server_port, silent=True)
        self.server.start_background()
        
        time.sleep(3)
        
        # 測試連線
        test_client = SimulationClient(port=self.server_port, silent=True)
        if test_client.connect(message="test"):
            print("✅ Server 已啟動")
        else:
            raise RuntimeError("❌ Server 啟動失敗")
        
        print("=" * 60)
    
    def run(self):
        """執行模擬（根據模式選擇）"""
        if self.mode == 'replay':
            self._run_replay()
        else:
            self._run_statistical()
    
    def _run_replay(self):
        """序列重放模式"""
        print("\n開始重放序列...")
        print("=" * 60)
        # 準備封包序列
        packet_sizes = self.features['packet_sizes']
        intervals = self.features['intervals']
        # 限制數量
        if self.max_packets > 0:
            packet_sizes = packet_sizes[:self.max_packets]
            intervals = intervals[:self.max_packets-1]  # 間隔比封包少一個
        
        # 過濾小封包
        if self.skip_small:
            filtered = [(s, i) for s, i in zip(packet_sizes, intervals + [0]) if s >= 100]
            if filtered:
                packet_sizes = [s for s, i in filtered]
                intervals = [i for s, i in filtered[:-1]]
        
        total = len(packet_sizes)
        print(f"重放封包數: {total}")
        
        # 建立 Client
        client = SimulationClient(port=self.server_port, silent=True)
        
        self.stats['start_time'] = time.time()
        
        # 逐個重放
        for i, size in enumerate(packet_sizes):
            # 發送
            result = client.connect_with_size(size=size)
            
            if result:
                self.stats['successful_connections'] += 1
                self.stats['total_bytes'] += size
            else:
                self.stats['failed_connections'] += 1
            
            self.stats['total_connections'] += 1
            
            # 進度顯示（每 100 個）
            if (i + 1) % 100 == 0:
                progress = (i + 1) / total * 100
                print(f"進度: {i + 1}/{total} ({progress:.1f}%)")
            
            # 等待間隔
            if i < len(intervals):
                scaled_interval = intervals[i] * self.time_scale
                time.sleep(scaled_interval)
        
        self.stats['end_time'] = time.time()
        
        print("=" * 60)
        self._print_summary()
    
    def _run_statistical(self):
        """統計模擬模式（原有邏輯）"""
        if self.use_threading:
            self._run_statistical_threaded()
        else:
            self._run_statistical_single()
    
    def _run_statistical_single(self):
        """單執行緒統計模擬"""
        print("\n開始模擬（單執行緒）...")
        
        self.stats['start_time'] = time.time()
        
        for client_id in range(self.num_clients):
            print(f"[Client {client_id + 1}/{self.num_clients}] 開始...", end=" ")
            
            result = self._simulate_client(client_id)
            
            self.stats['successful_connections'] += result['success']
            self.stats['failed_connections'] += result['failed']
            self.stats['total_connections'] += result['success'] + result['failed']
            
            print(f"成功: {result['success']}, 失敗: {result['failed']}")
        
        self.stats['end_time'] = time.time()
        
        self._print_summary()
    
    def _run_statistical_threaded(self):
        """多執行緒統計模擬"""
        print("\n開始模擬（多執行緒）...")
        
        self.stats['start_time'] = time.time()
        
        threads = []
        results = []
        
        def worker(client_id, results_list):
            result = self._simulate_client(client_id)
            results_list.append(result)
        
        for client_id in range(self.num_clients):
            t = threading.Thread(
                target=worker,
                args=(client_id, results),
                daemon=True
            )
            threads.append(t)
            t.start()
            
            if len(threads) >= self.max_workers:
                for t in threads:
                    t.join()
                threads = []
        
        for t in threads:
            t.join()
        
        for result in results:
            self.stats['successful_connections'] += result['success']
            self.stats['failed_connections'] += result['failed']
            self.stats['total_connections'] += result['success'] + result['failed']
        
        self.stats['end_time'] = time.time()
        
        self._print_summary()
    
    def _simulate_client(self, client_id):
        """模擬單一 Client（用於 statistical 模式）"""
        client = SimulationClient(port=self.server_port, silent=True)
        
        success = 0
        failed = 0
        
        for i in range(self.connections_per_client):
            size_idx = random.randint(0, len(self.features['packet_sizes']) - 1)
            size = self.features['packet_sizes'][size_idx]
            
            result = client.connect_with_size(size=size)
            
            if result:
                success += 1
            else:
                failed += 1
            
            if i < self.connections_per_client - 1:
                interval = random.uniform(self.interval_range[0], self.interval_range[1])
                time.sleep(interval)
        
        return {
            'client_id': client_id,
            'success': success,
            'failed': failed
        }
    
    def stop(self):
        """停止模擬並清理"""
        if self.server:
            print("\n停止 Server...")
            self.server.stop()
            print("✅ Server 已停止")
    
    def _print_summary(self):
        """顯示統計摘要"""
        duration = self.stats['end_time'] - self.stats['start_time']
        success_rate = (self.stats['successful_connections'] / 
                       self.stats['total_connections'] * 100 
                       if self.stats['total_connections'] > 0 else 0)
        
        print("\n" + "=" * 60)
        print("📊 模擬統計")
        print("=" * 60)
        print(f"模式:         {self.mode.upper()}")
        print(f"總連線數:     {self.stats['total_connections']}")
        print(f"成功連線:     {self.stats['successful_connections']}")
        print(f"失敗連線:     {self.stats['failed_connections']}")
        print(f"成功率:       {success_rate:.2f}%")
        
        if self.mode == 'replay' and self.stats['total_bytes'] > 0:
            print(f"總流量:       {self.stats['total_bytes']:,} bytes ({self.stats['total_bytes']/1024:.2f} KB)")
        
        print(f"實際時長:     {duration:.2f} 秒")
        print(f"平均速率:     {self.stats['total_connections']/duration:.2f} conn/s")
        print("=" * 60)


if __name__ == "__main__":
    print("測試 TrafficSimulator\n")
    
    try:
        simulator = TrafficSimulator()
        simulator.setup()
        simulator.run()
        simulator.stop()
        
        print("\n✅ TrafficSimulator 測試完成")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  收到中斷信號")
        if 'simulator' in locals() and simulator.server:
            simulator.stop()
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()