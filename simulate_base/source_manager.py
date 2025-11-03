"""
流量來源管理器

負責載入和管理流量特徵來源（JSON/PCAP）
支援連線級別的特徵檔案
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
        self.config_path = config_path
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
            
            # 只支援 JSON
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
        
        支援兩種格式：
        1. 連線級別 (connections.json) - 推薦 ⭐
        2. 封包級別 (features.json) - 舊格式（向後兼容）
        
        Returns:
            dict: 完整的特徵資料
                連線級別格式：
                {
                    'metadata': {...},
                    'statistics': {...},
                    'connections': [...]  # ← 關鍵欄位
                }
                
                封包級別格式（舊）：
                {
                    'packet_sizes': [...],
                    'intervals': [...],
                    'statistics': {...}
                }
        """
        if not self.sources:
            raise ValueError("沒有可用的來源")
        
        # 使用第一個來源
        source = self.sources[0]
        data = source['data']
        
        # 檢測格式類型
        if 'connections' in data:
            # 新格式：連線級別 ✅
            print(f"✅ 檢測到連線級別特徵檔案")
            self.features = data  # 直接返回完整資料
            return data
        
        elif 'packet_size_sample' in data or 'packet_sizes' in data:
            # 舊格式：封包級別（向後兼容）
            print(f"⚠️  檢測到舊格式封包級別特徵檔案")
            features = {
                'packet_sizes': data.get('packet_size_sample', data.get('packet_sizes', [])),
                'intervals': data.get('interval_sample', data.get('intervals', [])),
                'total_packets': data.get('total_packets', 0),
                'statistics': data.get('statistics', {})
            }
            self.features = features
            return features
        
        else:
            raise ValueError(
                f"無法識別的特徵檔案格式。\n"
                f"請確保檔案包含 'connections' (新格式) 或 'packet_sizes' (舊格式)。\n"
                f"使用 connection_analyzer.py 生成新格式檔案。"
            )
    
    def get_config(self):
        """
        取得配置
        
        Returns:
            dict: 配置字典
        """
        return self.config
    
    def get_summary(self):
        """取得來源摘要"""
        if not self.features:
            self.get_features()
        
        # 根據格式返回不同的摘要
        if 'connections' in self.features:
            # 連線級別摘要
            stats = self.features.get('statistics', {})
            return {
                'format': 'connection_level',
                'sources_count': len(self.sources),
                'total_connections': stats.get('total_connections', 0),
                'total_packets': stats.get('total_packets', 0),
                'total_bytes': stats.get('total_bytes', 0),
                'total_duration': stats.get('total_duration', 0),
                'by_protocol': stats.get('by_protocol', {})
            }
        else:
            # 封包級別摘要（舊格式）
            return {
                'format': 'packet_level',
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
        
        print("\n" + "=" * 60)
        print("來源摘要")
        print("=" * 60)
        print(f"格式類型:     {summary.get('format', 'unknown')}")
        print(f"來源數量:     {summary['sources_count']}")
        
        if summary.get('format') == 'connection_level':
            print(f"總連線數:     {summary['total_connections']}")
            print(f"總封包數:     {summary['total_packets']}")
            print(f"總流量:       {summary['total_bytes']:,} bytes ({summary['total_bytes']/1024/1024:.2f} MB)")
            print(f"總持續時間:   {summary['total_duration']:.2f} 秒")
            
            if summary.get('by_protocol'):
                print(f"\n協議分布:")
                for proto, data in summary['by_protocol'].items():
                    print(f"  {proto:8} - {data['count']:3} 連線, {data['bytes']/1024/1024:6.2f} MB")
        else:
            print(f"總封包數:     {summary['total_packets']}")
            print(f"平均封包大小: {summary['avg_packet_size']:.2f} bytes")
            print(f"平均間隔:     {summary['avg_interval']:.4f} 秒")
        
        print("=" * 60)
        
        print("\n✅ SourceManager 測試通過")
        
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()