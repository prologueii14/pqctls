# PQC-TLS 流量生成系統配置指南

## 📋 目錄結構

```
configs/
├── README.md                    # 本文檔
├── traffic_patterns.yaml        # 全域流量模式定義
└── experiments/                 # 實驗配置目錄
    ├── exp_00_quick_test.yaml          # 快速測試
    ├── exp_01_benign.yaml              # 正常流量測試
    ├── exp_02_packet_size_test.yaml    # 封包大小測試
    ├── exp_03_burst_test.yaml          # 突發流量測試
    ├── exp_04_stress_test.yaml         # 壓力測試
    └── exp_05_mixed_traffic.yaml       # 混合流量模擬
```

---

## 🎯 配置系統架構

### 兩層配置結構

1. **全域配置** (`traffic_patterns.yaml`)
   - 定義基礎流量模式的預設值
   - 設定 PQC-TLS 伺服器參數
   - 設定封包捕獲選項

2. **實驗配置** (`experiments/*.yaml`)
   - 定義實驗執行順序
   - 覆寫特定流量模式的參數
   - 控制實驗流程

---

## 📝 實驗配置格式

### 基本結構

```yaml
name: "實驗名稱"
description: "實驗描述"

sequences:
  - pattern: 流量模式名稱
    override:
      參數名稱: 覆寫值
    wait: 等待秒數
```

### 可用的流量模式

| 模式名稱 | 描述 | 預設特徵 |
|---------|------|---------|
| `web_browsing` | 網頁瀏覽 | 中等封包 (100-5000 bytes)，中頻 (0.5-3s) |
| `video_streaming` | 影片串流 | 大封包 (5000-50000 bytes)，高頻 (0.1-0.5s) |
| `file_download` | 檔案下載 | 超大封包 (10000-100000 bytes)，突發模式 |
| `gaming` | 遊戲流量 | 小封包 (50-500 bytes)，超高頻 (0.05-0.2s) |

---

## ⚙️ 可調整參數

### override 區塊支援的參數

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `connections` | 整數 | 連線數量 | `10`, `50`, `100` |
| `size.min` | 整數 | 最小封包大小 (bytes) | `50`, `100`, `1000` |
| `size.max` | 整數 | 最大封包大小 (bytes) | `500`, `5000`, `100000` |
| `interval.min` | 浮點數 | 最小時間間隔 (秒) | `0.05`, `0.5`, `1.0` |
| `interval.max` | 浮點數 | 最大時間間隔 (秒) | `0.2`, `3.0`, `5.0` |
| `burst` | 布林值 | 突發模式開關 | `true`, `false` |

### 參數覆寫範例

```yaml
sequences:
  - pattern: web_browsing
    override:
      connections: 50           # 覆寫連線數
      size:
        min: 500
        max: 3000              # 覆寫封包大小範圍
      interval:
        min: 0.3
        max: 2.0               # 覆寫時間間隔
      burst: true              # 啟用突發模式
    wait: 2                    # 完成後等待 2 秒
```

---

## 🔧 全域設定

### 修改 `traffic_patterns.yaml`

#### 伺服器設定

```yaml
server:
  port: 4433                      # 伺服器埠號
  kem_algorithm: "mlkem768"       # KEM 演算法
  sig_algorithm: "mldsa65"        # 簽名演算法
  keylog_file: "data/keys/server_keylog.log"
```

#### 支援的 PQC 演算法

**KEM 演算法** (`kem_algorithm`)：
- `mlkem512` - ML-KEM-512 (輕量級)
- `mlkem768` - ML-KEM-768 (平衡) ⭐ 預設
- `mlkem1024` - ML-KEM-1024 (高安全)

**簽名演算法** (`sig_algorithm`)：
- `mldsa44` - ML-DSA-44 (輕量級)
- `mldsa65` - ML-DSA-65 (平衡) ⭐ 預設
- `mldsa87` - ML-DSA-87 (高安全)

#### 封包捕獲設定

```yaml
capture:
  enabled: true                              # 啟用自動捕獲
  output_dir: "data/pcaps"                   # 輸出目錄
  interface: "\\Device\\NPF_Loopback"        # 捕獲介面
```

---

## 🚀 使用方法

### 執行實驗

```bash
# 基本用法
python traffic_generator.py configs/experiments/實驗檔案.yaml

# 範例
python traffic_generator.py configs/experiments/exp_00_quick_test.yaml
python traffic_generator.py configs/experiments/exp_01_benign.yaml
python traffic_generator.py configs/experiments/exp_02_packet_size_test.yaml
```

### 輸出檔案

執行後會自動產生：

1. **PCAP 檔案**
   - 位置：`data/pcaps/`
   - 格式：`實驗名稱_時間戳.pcap`
   - 範例：`exp_00_quick_test_20251113_015248.pcap`

2. **Keylog 檔案**
   - 位置：`data/keys/server_keylog.log`
   - 用途：Wireshark TLS 解密

---

## 📊 流量模式特徵分析

### 封包大小差異

| 流量模式 | 封包大小範圍 | 實際應用場景 |
|---------|------------|------------|
| Gaming | 50-500 bytes | 遊戲指令、即時通訊 |
| Web Browsing | 100-5000 bytes | HTML、CSS、小圖片 |
| Video Streaming | 5000-50000 bytes | 影片串流、音訊串流 |
| File Download | 10000-100000 bytes | 大檔案傳輸 |

### 時間間隔差異

| 流量模式 | 時間間隔 | 傳輸特性 |
|---------|---------|---------|
| Gaming | 0.05-0.2s | 超高頻、低延遲 |
| Video Streaming | 0.1-0.5s | 高頻、持續傳輸 |
| Web Browsing | 0.5-3.0s | 中頻、間歇性 |
| File Download | 1.0-5.0s | 低頻、大量資料 |

### 突發模式 (Burst)

- `burst: false` - 均勻分布，穩定間隔
- `burst: true` - 70% 機率瞬間爆發，30% 正常間隔

---

## 💡 實驗設計建議

### 1. 測試封包大小影響

創建實驗測試不同封包大小對 PQC-TLS 握手和傳輸的影響：

```yaml
sequences:
  - pattern: gaming
    override:
      connections: 20
      size: {min: 50, max: 200}    # 超小封包

  - pattern: web_browsing
    override:
      connections: 20
      size: {min: 1000, max: 5000}  # 中等封包

  - pattern: file_download
    override:
      connections: 20
      size: {min: 10000, max: 50000}  # 大封包
```

### 2. 測試連線頻率影響

```yaml
sequences:
  - pattern: gaming
    override:
      connections: 50
      interval: {min: 0.01, max: 0.05}  # 超高頻

  - pattern: gaming
    override:
      connections: 50
      interval: {min: 0.5, max: 1.0}    # 低頻
```

### 3. 測試突發流量

```yaml
sequences:
  - pattern: web_browsing
    override:
      connections: 30
      burst: false    # 正常模式
    wait: 3

  - pattern: web_browsing
    override:
      connections: 30
      burst: true     # 突發模式
```

### 4. 測試混合流量

模擬真實網路環境的混合流量：

```yaml
sequences:
  - pattern: web_browsing
    override: {connections: 10}

  - pattern: video_streaming
    override: {connections: 20}
    wait: 1

  - pattern: gaming
    override: {connections: 30}

  - pattern: file_download
    override: {connections: 5}
```

---

## 🔬 Wireshark 分析

### 設定解密

1. 開啟 Wireshark 偏好設定
2. 前往：`Edit` → `Preferences` → `Protocols` → `TLS`
3. 設定 `(Pre)-Master-Secret log filename`：
   ```
   H:\Workspace\NYCU\Code\pqctls\data\keys\server_keylog.log
   ```

### 過濾器

```
tcp.port == 4433                  # 只看 PQC-TLS 流量
tls.handshake                     # 只看 TLS 握手
tls.record.content_type == 23     # 只看應用資料
```

### 重點觀察項目

1. **PQC 握手封包大小**
   - ML-KEM-768 ClientKeyExchange: ~1323 bytes
   - ML-DSA-65 CertificateVerify: ~3309 bytes

2. **握手時間**
   - 完整握手通常需要 4-6 個 RTT

3. **應用資料封包**
   - 使用 TLS 1.3 記錄層加密
   - 解密後可看到明文內容

---

## 📁 檔案清單

### 已提供的實驗配置

| 檔案 | 描述 | 連線數 | 用途 |
|------|------|-------|------|
| `exp_00_quick_test.yaml` | 快速測試 | 8 | 驗證系統正常運作 |
| `exp_01_benign.yaml` | 正常流量 | 65 | 完整正常流量測試 |
| `exp_02_packet_size_test.yaml` | 封包大小 | 30 | 測試封包大小影響 |
| `exp_03_burst_test.yaml` | 突發流量 | 40 | 測試突發模式 |
| `exp_04_stress_test.yaml` | 壓力測試 | 350 | 高負載測試 |
| `exp_05_mixed_traffic.yaml` | 混合流量 | 110 | 模擬真實環境 |

---

## 🐛 故障排除

### 問題：沒有產生 PCAP 檔案

**檢查項目：**
1. `traffic_patterns.yaml` 中 `capture.enabled: true`
2. `capture.interface` 設定為 `\\Device\\NPF_Loopback`
3. 確認 Npcap 已安裝並啟用 loopback 支援

### 問題：Wireshark 無法解密

**檢查項目：**
1. 確認 keylog 檔案存在：`data/keys/server_keylog.log`
2. 確認 Wireshark 設定的路徑是**絕對路徑**
3. 重新啟動 Wireshark 載入 keylog

### 問題：連線失敗

**檢查項目：**
1. 確認 port 4433 沒有被占用
2. 檢查防火牆設定
3. 確認 OpenSSL with OQS-Provider 正確安裝

---

## 📚 參考資料

- **NIST PQC 標準**: https://csrc.nist.gov/projects/post-quantum-cryptography
- **ML-KEM (Kyber)**: FIPS 203
- **ML-DSA (Dilithium)**: FIPS 204
- **liboqs**: https://github.com/open-quantum-safe/liboqs
- **oqs-provider**: https://github.com/open-quantum-safe/oqs-provider

---

## 📧 問題回報

如有問題或建議，請在專案中提出 Issue。
