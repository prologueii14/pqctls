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
        
        # 拓樸配置
        self.num_clients = self.config['topology']['clients']
        self.server_port = self.config['topology']['server_port']
        self.connections_per_client = self.config['topology']['per_client']['connections']
        self.interval_range = self.config['topology']['per_client']['interval_range']
        
        # 模擬配置
        self.duration = self.config['simulation']['duration']
        self.mode = self.config['simulation']['mode']
        self.use_threading = self.config['simulation']['execution']['threading']
        self.max_workers = self.config['simulation']['execution']['max_workers']
        
        # Server
        self.server = None
        
        # 統計
        self.stats = {
            'total_connections': 0,
            'successful_connections': 0,
            'failed_connections': 0,
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
        
        print(f"\n模擬配置:")
        print(f"  Client 數量:  {self.num_clients}")
        print(f"  每 Client 連線: {self.connections_per_client}")
        print(f"  總連線數:     {self.num_clients * self.connections_per_client}")
        print(f"  模擬時長:     {self.duration} 秒")
        print(f"  多執行緒:     {'啟用' if self.use_threading else '禁用'}")
        
        # 啟動 Server
        print(f"\n啟動 Server (Port: {self.server_port})...")
        self.server = SimulationServer(
            port=self.server_port,
            silent=True
        )
        
        print("   開始 start_background()...")
        self.server.start_background()
        
        print(f"   等待 3 秒...")
        time.sleep(3)
        
        # Debug：檢查狀態
        print(f"   Server.is_running: {self.server.is_running}")
        print(f"   Server.server_thread: {self.server.server_thread}")
        if self.server.server_thread:
            print(f"   Thread.is_alive(): {self.server.server_thread.is_alive()}")
        print(f"   Server.is_alive(): {self.server.is_alive()}")
        
        if self.server.is_alive():
            print("✅ Server 已啟動")
        else:
            print("❌ Server 未正常啟動")
            # 不直接拋錯，先看狀態
            print("   嘗試測試連線...")
            
            # 測試連線看看
            test_client = SimulationClient(port=self.server_port, silent=True)
            result = test_client.connect(message="test")
            print(f"   測試連線結果: {result}")
            
            if not result:
                raise RuntimeError("❌ Server 啟動失敗")
        
        print("=" * 60)
    
    def _simulate_client(self, client_id):
        """
        模擬單一 Client 的行為
        
        Args:
            client_id: Client 編號
            
        Returns:
            dict: 統計資訊
        """
        client = SimulationClient(port=self.server_port, silent=True)
        
        success = 0
        failed = 0
        
        for i in range(self.connections_per_client):
            # 選擇封包大小（從特徵中隨機選）
            size_idx = random.randint(0, len(self.features['packet_sizes']) - 1)
            size = self.features['packet_sizes'][size_idx]
            
            # 連線
            result = client.connect_with_size(size=size)
            
            if result:
                success += 1
            else:
                failed += 1
            
            # 間隔（從範圍中隨機選）
            if i < self.connections_per_client - 1:
                interval = random.uniform(self.interval_range[0], self.interval_range[1])
                time.sleep(interval)
        
        return {
            'client_id': client_id,
            'success': success,
            'failed': failed
        }
    
    def run(self):
        """執行模擬（單執行緒版）"""
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
    
    def run_threaded(self):
        """執行模擬（多執行緒版）"""
        print("\n開始模擬（多執行緒）...")
        
        self.stats['start_time'] = time.time()
        
        threads = []
        results = []
        
        def worker(client_id, results_list):
            result = self._simulate_client(client_id)
            results_list.append(result)
        
        # 建立執行緒
        for client_id in range(self.num_clients):
            t = threading.Thread(
                target=worker,
                args=(client_id, results),
                daemon=True
            )
            threads.append(t)
            t.start()
            
            # 控制並行數量
            if len(threads) >= self.max_workers:
                for t in threads:
                    t.join()
                threads = []
        
        # 等待剩餘執行緒
        for t in threads:
            t.join()
        
        # 統計結果
        for result in results:
            self.stats['successful_connections'] += result['success']
            self.stats['failed_connections'] += result['failed']
            self.stats['total_connections'] += result['success'] + result['failed']
        
        self.stats['end_time'] = time.time()
        
        self._print_summary()
    
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
        print(f"總連線數:     {self.stats['total_connections']}")
        print(f"成功連線:     {self.stats['successful_connections']}")
        print(f"失敗連線:     {self.stats['failed_connections']}")
        print(f"成功率:       {success_rate:.2f}%")
        print(f"實際時長:     {duration:.2f} 秒")
        print(f"平均速率:     {self.stats['total_connections']/duration:.2f} conn/s")
        print("=" * 60)


if __name__ == "__main__":
    print("測試 TrafficSimulator\n")
    
    try:
        simulator = TrafficSimulator()
        simulator.setup()
        
        if simulator.use_threading:
            simulator.run_threaded()
        else:
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