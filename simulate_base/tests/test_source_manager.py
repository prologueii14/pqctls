"""
SourceManager 單元測試
"""

import sys
import os

# 加入父目錄到 path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from source_manager import SourceManager


def test_load_config():
    """測試配置載入"""
    print("\n測試: 載入配置")
    mgr = SourceManager()
    assert mgr.config is not None
    assert 'sources' in mgr.config
    print("✅ 通過")


def test_load_sources():
    """測試來源載入"""
    print("\n測試: 載入來源")
    mgr = SourceManager()
    assert len(mgr.sources) > 0
    print(f"✅ 通過（載入 {len(mgr.sources)} 個來源）")


def test_get_features():
    """測試特徵提取"""
    print("\n測試: 提取特徵")
    mgr = SourceManager()
    features = mgr.get_features()
    
    assert 'packet_sizes' in features
    assert 'intervals' in features
    assert len(features['packet_sizes']) > 0
    assert len(features['intervals']) > 0
    
    print(f"✅ 通過（封包樣本: {len(features['packet_sizes'])}）")


def test_get_summary():
    """測試摘要"""
    print("\n測試: 取得摘要")
    mgr = SourceManager()
    summary = mgr.get_summary()
    
    assert 'sources_count' in summary
    assert 'total_packets' in summary
    assert summary['total_packets'] > 0
    
    print(f"✅ 通過（總封包: {summary['total_packets']}）")


if __name__ == "__main__":
    print("=" * 60)
    print("SourceManager 單元測試")
    print("=" * 60)
    
    try:
        test_load_config()
        test_load_sources()
        test_get_features()
        test_get_summary()
        
        print("\n" + "=" * 60)
        print("✅ 所有測試通過")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ 測試失敗: {e}")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()