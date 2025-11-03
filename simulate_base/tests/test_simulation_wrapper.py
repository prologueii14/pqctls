"""
Client/Server 包裝測試
"""

import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from simulation_client import SimulationClient
from simulation_server import SimulationServer
import time


def test_server_start_stop():
    """測試 Server 啟動和停止"""
    print("\n測試: Server 啟動/停止")
    
    server = SimulationServer(port=8443, silent=True)
    server.start_background()
    assert server.is_running == True
    
    time.sleep(1)
    
    server.stop()
    assert server.is_running == False
    
    print("✅ 通過")


def test_client_connect():
    """測試 Client 連線"""
    print("\n測試: Client 連線")
    
    # 啟動 Server
    server = SimulationServer(port=8444, silent=True)
    server.start_background()
    
    time.sleep(2)
    
    # Client 連線
    client = SimulationClient(port=8444, silent=True)
    result = client.connect(message="test")
    
    assert result == True
    
    # 停止 Server
    server.stop()
    
    print("✅ 通過")


def test_client_with_size():
    """測試指定大小訊息"""
    print("\n測試: 指定大小訊息")
    
    # 啟動 Server
    server = SimulationServer(port=8445, silent=True)
    server.start_background()
    
    time.sleep(2)
    
    # 測試不同大小
    client = SimulationClient(port=8445, silent=True)
    
    result1 = client.connect_with_size(size=100)
    assert result1 == True
    
    result2 = client.connect_with_size(size=1500)
    assert result2 == True
    
    # 停止 Server
    server.stop()
    
    print("✅ 通過")


if __name__ == "__main__":
    print("=" * 60)
    print("Client/Server 包裝測試")
    print("=" * 60)
    
    try:
        test_server_start_stop()
        test_client_connect()
        test_client_with_size()
        
        print("\n" + "=" * 60)
        print("✅ 所有測試通過")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ 測試失敗: {e}")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()