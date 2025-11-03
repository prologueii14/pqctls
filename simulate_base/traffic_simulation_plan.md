# Wireshark 封包錄製與 Python 分析模擬規劃

**建立日期**: 2025-11-02  
**目的**: 在現有 PQC-TLS 框架中，透過分析真實流量特徵，模擬真實的網路行為模式

---

## 🎯 目標

在現有 PQC-TLS 框架中，透過分析真實流量特徵，模擬真實的網路行為模式。

---

## 📊 工作流程
```
Phase 1: 錄製真實流量
   ↓
Phase 2: 提取行為特徵
   ↓
Phase 3: 實作模擬器
   ↓
Phase 4: 驗證相似度
```

---

## Phase 1: 錄製真實流量（Wireshark）

### 1.1 準備工作
- [ ] 安裝 Wireshark
- [ ] 確認 Npcap 已安裝
- [ ] 確認可以捕獲 localhost 流量

### 1.2 錄製自己的 PQC-TLS 流量
- [ ] 啟動 Server (`normal_server.py`)
- [ ] 開啟 Wireshark，選擇 Loopback 介面
- [ ] 設定過濾器：`tcp.port == 8443`
- [ ] 執行多次 Client 連線（模擬不同使用場景）
- [ ] 儲存為 `<date>/baseline_traffic_<number>.pcap`

### 1.3 錄製參考流量（可選）
- [ ] 訪問真實 HTTPS 網站（如 google.com）
- [ ] 錄製 10-20 個請求
- [ ] 儲存為 `<date>/reference_https_<number>.pcap`

---

## Phase 2: 提取行為特徵（Python）

### 2.1 建立分析工具 `simulate_base/traffic_analyzer.py`

**功能**：
- 讀取 PCAP 檔案
- 提取封包大小分布
- 提取時間間隔
- 提取 TCP flags 序列
- 輸出統計報告

### 2.2 需要提取的特徵

- [ ] 封包大小（bytes）
- [ ] 封包間隔時間（秒）
- [ ] 每個連線的封包數
- [ ] 請求/回應模式
- [ ] TLS 握手時間

### 2.3 輸出格式
```python
features = {
    'packet_sizes': [100, 1500, 200, ...],
    'intervals': [0.01, 0.05, 0.02, ...],
    'patterns': [...]
}
```

---

## Phase 3: 實作流量模擬器

### 3.1 建立 `simulate_base/traffic_simulator.py`

**功能**：
- 載入提取的特徵
- 根據特徵生成請求
- 控制封包大小和時序

### 3.2 模擬策略

- [ ] 基礎模式：固定大小、固定間隔
- [ ] 統計模式：根據分布隨機生成
- [ ] 重放模式：精確重現時序

### 3.3 整合到現有框架

- [ ] 後續能使用 `normal_client.py` 發送請求
- [ ] 後續能使用 `traffic_capture.py` 捕獲模擬流量
- [ ] 比對原始流量和模擬流量

---

## Phase 4: 驗證相似度

### 4.1 比較指標

- [ ] 封包大小分布（統計）
- [ ] 時間間隔分布（統計）
- [ ] 總流量大小
- [ ] 連線模式

### 4.2 建立 `utils/traffic_comparator.py`

**功能**：
- 比較兩個 PCAP 的特徵
- 計算相似度分數
- 生成視覺化報告

---

## 📁 產出檔案結構
```
pqctls/
├── data/
│   ├── reference_pcaps/        # 參考流量
│   │   ├── baseline_traffic.pcap
│   │   └── reference_https.pcap
│   │
│   ├── features/               # 提取的特徵
│   │   ├── baseline_features.json
│   │   └── reference_features.json
│   │
│   └── simulated_pcaps/        # 模擬產生的流量
│       └── simulated_*.pcap
│
├── utils/
│   ├── traffic_analyzer.py     # 特徵提取
│   └── traffic_comparator.py   # 相似度比較
│
└── experiments/
    ├── traffic_simulator.py    # 流量模擬器
    └── validate_simulation.py  # 驗證腳本
```

---

## ✅ 完成標準

- [ ] 能從 PCAP 提取至少 5 種特徵
- [ ] 能根據特徵生成模擬流量
- [ ] 模擬流量與原始流量的相似度 > 80%
- [ ] 有完整的比較報告

---

## 🎯 關鍵決策點

### Q1: 要模擬多真實？
- **簡單**：只模擬封包大小和數量
- **中等**：加上時間間隔
- **完整**：包含所有統計特徵

### Q2: 使用哪種參考流量？
- 自己的 PQC-TLS 流量（更相關）
- 真實 HTTPS 流量（更真實）
- 兩者混合

### Q3: 模擬的粒度？
- 連線級別（整個 session）
- 封包級別（每個封包）

---

## ⏱️ 預估時間

| 階段 | 預估時間 |
|------|---------|
| Phase 1 | 30 分鐘 |
| Phase 2 | 2-3 小時 |
| Phase 3 | 3-4 小時 |
| Phase 4 | 1-2 小時 |
| **總計** | **7-10 小時** |

---

## 📝 進度追蹤

### Phase 1
- [ ] 完成準備工作
- [ ] 錄製 PQC-TLS 流量
- [ ] 錄製參考流量（可選）

### Phase 2
- [ ] 完成 `simulate_base/traffic_analyzer.py`
- [ ] 提取所有必要特徵
- [ ] 生成特徵報告

### Phase 3
- [ ] 完成 `simulate_base/traffic_simulator.py`
- [ ] 實作所有模擬策略
- [ ] 整合到現有框架

### Phase 4
- [ ] 完成 `simulate_base/traffic_comparator.py`
- [ ] 計算相似度
- [ ] 生成驗證報告

---

## 📚 參考資源

### Wireshark
- 官方文檔: https://www.wireshark.org/docs/
- 過濾器語法: https://wiki.wireshark.org/DisplayFilters

### Scapy
- 官方文檔: https://scapy.readthedocs.io/
- PCAP 操作: https://scapy.readthedocs.io/en/latest/usage.html#reading-pcap-files

### 相關論文
- TLS 流量分析
- 網路流量特徵提取
- 流量模擬技術

---

**最後更新**: 2025-11-02