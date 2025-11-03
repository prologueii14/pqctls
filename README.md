# 流量模擬系統

## 🎯 目標

將真實世界的 HTTPS 流量特徵，轉換為基於 PQC-TLS 的正常流量資料集。

---

## 🏗️ 系統架構
```
真實流量 (PCAP/JSON)
    ↓
source_manager.py (載入特徵)
    ↓
traffic_simulator.py (調度模擬)
    ↓
simulation_client/server.py (執行連線)
    ↓
dataset_builder.py (捕獲流量)
    ↓
PQC-TLS 流量資料集 (PCAP)
    ↓
analyzer.py (事後分析)
```

---

## 📁 目錄結構
```
simulate_base/
├── README.md                   # 本文檔
├── IMPLEMENTATION_PLAN.md      # 實作計劃
├── API_REFERENCE.md            # API 文檔
│
├── simulation_config.yaml      # 模擬配置
├── run_simulation.py           # 主腳本
├── analyze_dataset.py          # 分析腳本
│
├── source_manager.py           # 來源管理
├── traffic_simulator.py        # 模擬引擎
├── dataset_builder.py          # 資料集建構
├── analyzer.py                 # 分析器
│
├── simulation_client.py        # Client 包裝
├── simulation_server.py        # Server 包裝
│
├── wireshark/                  # 原始 PCAP（手動放置）
│   ├── 20251104.pcap
│   └── normal_browsing_30s.pcap
│
├── features/                   # 提取的特徵（手動產生）
│   ├── 20251104_features.json
│   └── normal_browsing_30s_features.json
│
├── datasets/                   # 產出的資料集（自動生成）
│   └── sim_YYYYMMDD_NNN/
│       ├── traffic.pcap
│       └── metadata.json
│
└── tests/                      # 測試
    ├── test_source_manager.py
    ├── test_simulator.py
    └── ...
```

---

## 🚀 快速開始

### 1. 準備來源
```bash
# 手動：用 Wireshark 抓包
# 儲存到 simulate_base/wireshark/

# 手動：提取特徵
python traffic_analyzer.py wireshark/xxx.pcap
# 產生 features/xxx_features.json
```

### 2. 配置模擬

編輯 `simulation_config.yaml`：
```yaml
sources:
  - type: "json"
    path: "features/normal_browsing_30s_features.json"
    weight: 1.0

simulation:
  duration: 30
  
topology:
  clients: 5
  connections_per_client: 10
```

### 3. 執行模擬
```bash
python run_simulation.py
# 自動完成捕獲並儲存到 datasets/
```

### 4. 分析結果
```bash
python analyze_dataset.py
# 指定 dataset_dir 在腳本內
```

---

## 🔧 配置說明

### `simulation_config.yaml` 參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `simulation.mode` | 模擬模式（statistical/replay） | statistical |
| `simulation.duration` | 持續時間（秒） | 30 |
| `topology.clients` | Client 數量 | 5 |
| `topology.connections_per_client` | 每個 Client 的連線數 | 10 |
| `execution.threading` | 是否多執行緒 | true |

詳細參數見 `API_REFERENCE.md`

---

## 📊 產出格式

### 資料集結構
```
datasets/sim_20251104_001/
├── traffic.pcap          # 捕獲的流量
└── metadata.json         # 模擬資訊
```

### metadata.json 內容
```json
{
  "timestamp": "2025-11-04T15:30:00",
  "duration": 30,
  "sources": ["normal_browsing_30s_features.json"],
  "config": {...},
  "statistics": {
    "total_packets": 1234,
    "total_connections": 50
  }
}
```

---

## 🧪 測試
```bash
# 執行所有測試
python -m pytest tests/

# 執行特定測試
python tests/test_source_manager.py
```

---

## 🔄 工作流程
```
階段 1: 準備（手動）
  ✓ Wireshark 抓包
  ✓ traffic_analyzer.py 提取特徵

階段 2: 配置（手動）
  ✓ 編輯 simulation_config.yaml

階段 3: 模擬（自動）
  ✓ python run_simulation.py

階段 4: 分析（手動觸發）
  ✓ python analyze_dataset.py
```

---

## 📚 參考文檔

- 實作計劃：`IMPLEMENTATION_PLAN.md`
- API 文檔：`API_REFERENCE.md`
- 整體架構：`../architecture.md`