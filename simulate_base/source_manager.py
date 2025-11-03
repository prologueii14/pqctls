"""
流量來源管理器

負責載入和管理流量特徵來源（JSON/PCAP）
"""

import os
import json
import yaml
from pathlib import Path


class SourceManager:
    """流量來源管理器"""
    
    def __init__(self, config_path='simulate_base/simulation_config.yaml'):
        """
        初始化
        
        Args:
            config_path: 配置檔路徑
        """
        self.config = self._load_config(config_path)
        self.sources = []
        self.features = None
        
        self._load_sources()
    
    def _load_config(self, config_path):
        """載入配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_sources(self):
        """載入所有來源"""
        sources_config = self.config.get('sources', [])
        
        for src_config in sources_config:
            if not src_config.get('enabled', True):
                continue
            
            src_type = src_config['type']
            src_path = src_config['path']
            
            # Phase 1: 只支援 JSON
            if src_type == 'json':
                self._load_json_source(src_path)
            else:
                print(f"⚠️  暫不支援類型: {src_type}")
    
    def _load_json_source(self, path):
        """載入 JSON 特徵檔案"""
        full_path = Path('simulate_base') / path
        
        if not full_path.exists():
            raise FileNotFoundError(f"找不到檔案: {full_path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.sources.append({
            'type': 'json',
            'path': str(full_path),
            'data': data
        })
        
        print(f"✅ 載入來源: {path}")
    
    def get_features(self):
        """
        取得流量特徵
        
        Returns:
            dict: {
                'packet_sizes': [100, 1500, ...],
                'intervals': [0.01, 0.05, ...],
                'total_packets': 1000
            }
        """
        if not self.sources:
            raise ValueError("沒有可用的來源")
        
        # Phase 1: 只使用第一個來源
        source = self.sources[0]
        data = source['data']
        
        # 提取關鍵特徵
        features = {
            'packet_sizes': data.get('packet_size_sample', []),
            'intervals': data.get('interval_sample', []),
            'total_packets': data.get('total_packets', 0),
            'statistics': data.get('statistics', {})
        }
        
        self.features = features
        return features
    
    def get_summary(self):
        """取得來源摘要"""
        if not self.features:
            self.get_features()
        
        return {
            'sources_count': len(self.sources),
            'total_packets': self.features.get('total_packets', 0),
            'avg_packet_size': self.features['statistics'].get('avg_packet_size', 0),
            'avg_interval': self.features['statistics'].get('avg_interval', 0)
        }


# ============================================
# 測試用
# ============================================
if __name__ == "__main__":
    print("測試 SourceManager\n")
    
    try:
        mgr = SourceManager()
        features = mgr.get_features()
        summary = mgr.get_summary()
        
        print("=" * 60)
        print("來源摘要")
        print("=" * 60)
        print(f"來源數量:     {summary['sources_count']}")
        print(f"總封包數:     {summary['total_packets']}")
        print(f"平均封包大小: {summary['avg_packet_size']:.2f} bytes")
        print(f"平均間隔:     {summary['avg_interval']:.4f} 秒")
        print("=" * 60)
        
        print("\n✅ SourceManager 測試通過")
        
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
