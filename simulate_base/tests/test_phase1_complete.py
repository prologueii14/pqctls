"""
Phase 1 完整驗收測試（Debug 版）
"""

import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from source_manager import SourceManager
from simulation_client import SimulationClient
from simulation_server import SimulationServer
import time


def test_phase1_integration():
    """Phase 1 完整整合測試"""
    
    print("\n" + "=" * 60)
    print("Phase 1 完整整合測試（Debug 版）")
    print("=" * 60)
    
    # 1. SourceManager
    print("\n[1/4] 測試 SourceManager")
    mgr = SourceManager()
    features = mgr.get_features()
    summary = mgr.get_summary()
    
    assert summary['total_packets'] > 0
    assert len(features['packet_sizes']) > 0
    print(f"   ✅ 載入 {summary['total_packets']} 個封包特徵")
    
    # 2. 啟動 Server
    print("\n[2/4] 啟動 SimulationServer")
    server = SimulationServer(port=8447, silent=False)  # 改成 False 看輸出
    print("   正在啟動...")
    server.start_background()
    
    print(f"   Server.is_running: {server.is_running}")
    print(f"   Server.is_alive(): {server.is_alive()}")
    
    if not server.is_alive():
        print("   ❌ Server 沒有正常啟動！")
        return
    
    print(f"   ✅ Server 運行中 (Port: 8447)")
    
    time.sleep(2)
    
    # 3. 多個 Client 連線
    print("\n[3/4] 測試多個 Client 連線")
    client = SimulationClient(port=8447, silent=True)
    
    success_count = 0
    test_count = 10
    
    for i in range(test_count):
        size = features['packet_sizes'][i % len(features['packet_sizes'])]
        
        print(f"   連線 {i+1}/{test_count} (size={size})...", end=" ")
        result = client.connect_with_size(size=size)
        
        if result:
            success_count += 1
            print("✅")
        else:
            print("❌")
        
        time.sleep(0.2)
    
    print(f"\n   總結: {success_count}/{test_count} 個連線成功")
    
    if success_count < test_count * 0.8:
        print(f"   ❌ 成功率不足 80%")
        return
    
    # 4. Server 仍在運行
    print("\n[4/4] 驗證 Server 持續性")
    print(f"   Server.is_running: {server.is_running}")
    print(f"   Server.is_alive(): {server.is_alive()}")
    
    if not server.is_alive():
        print(f"   ❌ Server 已停止運行")
        return
    
    print(f"   ✅ Server 仍在運行")
    
    # 清理
    print("\n清理資源...")
    server.stop()
    time.sleep(1)
    print(f"   Server.is_alive(): {server.is_alive()}")
    print(f"   ✅ Server 已停止")
    
    print("\n" + "=" * 60)
    print("✅ Phase 1 驗收測試通過")
    print("=" * 60)
    print("\n準備進入 Phase 2: 模擬引擎開發")


if __name__ == "__main__":
    try:
        test_phase1_integration()
    except AssertionError as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()