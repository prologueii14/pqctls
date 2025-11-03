"""
模擬用 Client 包裝

包裝 core/normal_client.py，提供適合批量模擬的介面
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.normal_client import TLSClient
import io
import contextlib


class SimulationClient:
    """模擬用 Client 包裝"""
    
    def __init__(self, host='localhost', port=8443, kem_algorithm=None, silent=True):
        """
        初始化
        
        Args:
            host: 目標主機
            port: 目標 port
            kem_algorithm: KEM 算法
            silent: 是否靜默模式（不印輸出）
        """
        self.host = host
        self.port = port
        self.kem_algorithm = kem_algorithm
        self.silent = silent
        
        self.client = TLSClient(host=host, port=port, kem_algorithm=kem_algorithm)
        
    def connect(self, message=None, timeout=10):
        """
        連接 Server
        
        Args:
            message: 要發送的訊息
            timeout: 超時時間
            
        Returns:
            bool: 是否成功
        """
        try:
            if self.silent:
                # 靜默模式：抑制所有輸出
                with contextlib.redirect_stdout(io.StringIO()), \
                     contextlib.redirect_stderr(io.StringIO()):
                    self.client.connect(message=message)
            else:
                self.client.connect(message=message)
            
            return True
            
        except Exception as e:
            if not self.silent:
                print(f"❌ 連線失敗: {e}")
            return False
    
    def connect_with_size(self, size=100, timeout=10):
        """
        發送指定大小的訊息
        
        Args:
            size: 訊息大小（bytes）
            timeout: 超時時間
            
        Returns:
            bool: 是否成功
        """
        # 生成指定大小的訊息
        message = "X" * min(size, 10000)  # 限制最大 10KB
        return self.connect(message=message, timeout=timeout)


# ============================================
# 測試用
# ============================================
if __name__ == "__main__":
    print("測試 SimulationClient\n")
    
    print("1. 測試靜默模式")
    client = SimulationClient(port=8443, silent=True)
    print("   （應該無輸出）")
    # result = client.connect(message="test")
    # print(f"   結果: {result}")
    
    print("\n2. 測試非靜默模式")
    client = SimulationClient(port=8443, silent=False)
    # result = client.connect(message="test")
    
    print("\n3. 測試指定大小訊息")
    client = SimulationClient(port=8443, silent=True)
    # result = client.connect_with_size(size=1500)
    # print(f"   發送 1500 bytes: {result}")
    
    print("\n✅ SimulationClient 測試完成")
    print("   （實際連線測試需要 Server 運行）")