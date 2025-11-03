"""
模擬用 Server 包裝

包裝 core/normal_server.py，提供背景執行功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.normal_server import TLSServer
import threading
import time


class SimulationServer:
    """模擬用 Server 包裝"""
    
    def __init__(self, port=8443, kem_algorithm=None, sig_algorithm=None, silent=True):
        """
        初始化
        
        Args:
            port: 監聽 port
            kem_algorithm: KEM 算法
            sig_algorithm: 簽章算法
            silent: 是否靜默模式
        """
        self.port = port
        self.kem_algorithm = kem_algorithm
        self.sig_algorithm = sig_algorithm
        self.silent = silent
        
        self.server = TLSServer(
            port=port,
            kem_algorithm=kem_algorithm,
            sig_algorithm=sig_algorithm
        )
        
        self.server_thread = None
        self.is_running = False
        
    def start_background(self):
        """背景啟動 Server（持續運行）"""
        if self.is_running:
            if not self.silent:
                print("⚠️  Server 已在運行")
            return
        
        def run_server():
            """Server 執行函數"""
            try:
                if self.silent:
                    # 完全抑制輸出
                    with open(os.devnull, 'w') as devnull:
                        old_stdout = sys.stdout
                        old_stderr = sys.stderr
                        sys.stdout = devnull
                        sys.stderr = devnull
                        try:
                            self.server.start()
                        finally:
                            sys.stdout = old_stdout
                            sys.stderr = old_stderr
                else:
                    self.server.start()
            except Exception as e:
                if not self.silent:
                    print(f"❌ Server 錯誤: {e}")
                self.is_running = False
        
        # 啟動執行緒
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.is_running = True
        
        # 等待 Server 啟動
        time.sleep(3)
        
        if not self.silent:
            print(f"✅ Server 已在背景啟動 (Port: {self.port})")
            print(f"   狀態: {'運行中' if self.is_running else '已停止'}")
    
    def stop(self):
        """停止 Server"""
        if not self.is_running:
            return
        
        try:
            self.server.stop()
            self.is_running = False
            
            # 等待執行緒結束
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=2)
            
            if not self.silent:
                print("✅ Server 已停止")
        except Exception as e:
            if not self.silent:
                print(f"⚠️  停止 Server 時出錯: {e}")
    
    def is_alive(self):
        """檢查 Server 是否還在運行"""
        return self.is_running and (self.server_thread and self.server_thread.is_alive())


if __name__ == "__main__":
    print("測試 SimulationServer\n")
    
    print("1. 啟動背景 Server（靜默模式）")
    server = SimulationServer(port=8443, silent=True)
    server.start_background()
    print(f"   Server 狀態: {server.is_alive()}")
    
    print("\n2. 持續運行 10 秒...")
    for i in range(10):
        time.sleep(1)
        print(f"   {i+1} 秒 - Server 狀態: {server.is_alive()}")
    
    print("\n3. 停止 Server")
    server.stop()
    print(f"   Server 狀態: {server.is_alive()}")
    
    print("\n✅ SimulationServer 測試完成")