# PQC-TLS 

## 📋 概述

本專案旨在研究 Post-Quantum Cryptography (PQC) + TLS 架構的安全性，通過實作各種攻擊手法來測試和分析 PQC-TLS ，並融合攻擊，產生類似於PCAP的加密流量資料集與加密惡意流量資料集。

**環境與套件**：
- OpenSSL + liboqs (PQC 實作)
- Python (主要開發語言)
- Windows + Anaconda 

---

### 研究目標

1. 建立完整的 PQC-TLS Client-Server 測試環境
2. 實作 攻擊手法（包含混合模式和純 PQC 模式）
3. 分析 PQC-TLS 的安全性和效能特性
4. 產出資料集，包含明碼流量、加密流量、加密惡意流量

---

## 系統架構

### 核心組件

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ malicious_client│ ─攻擊─> │   mitm_proxy    │ <─攻擊─ │ malicious_server│
│   (Client端)    │         │   (中間人)       │         │   (Server端)    │
└────────┬────────┘         └────────┬────────┘         └────────┬────────┘
         │                           │                           │
         │                           │                           │
         ▼                           ▼                           ▼
    攻擊 Server              攔截/修改/注入               攻擊 Client
```

### 核心程式 (6 隻)

| 程式 | 功能 | 發起位置 |
|------|------|---------|
| `normal_client.py` | 標準 TLS 客戶端，用於基準測試 | - |
| `normal_server.py` | 標準 TLS 伺服器，用於被測試 | - |
| `malicious_client.py` | 可配置的攻擊客戶端 | Client 端 |
| `malicious_server.py` | 可配置的攻擊伺服器 | Server 端 |
| `mitm_proxy.py` | 中間人攻擊代理 | 中間人 |
| `passive_monitor.py` | 被動流量監聽和分析 | 被動觀察 |

---

## 攻擊手法清單

### 統計摘要

| 類別 | 攻擊數量 | 主要發起位置 |
|------|---------|-------------|
| **PQC 特定** | 8 | Client, MITM, Passive |
| **側信道** | 7 | Passive, Local |
| **憑證攻擊** | 6 | MITM |
| **協議邏輯** | 7 | Client, Server, MITM |
| **實作漏洞** | 7 | Client, Server, MITM |
| **混合模式** | 4 | MITM |
| **DoS** | 6 | Client |
| **降級攻擊** | 5 | MITM |
| **流量分析** | 5 | Passive |
| **網路劣化** | 20+ | MITM |
| **總計** | **79+ 種** | - |

### 發起位置分布

```
Client:    ~25 種攻擊 (32%)
MITM:      ~35 種攻擊 (44%) 
Server:    ~10 種攻擊 (13%)
Passive:   ~15 種攻擊 (19%)
```

### A. PQC 特定攻擊

| 攻擊手法 | 發起位置 | 難度 |
|---------|---------|------|
| PQC 密鑰尺寸放大攻擊 | Client / Server | 中 |
| 混合模式降級攻擊 | MITM | 高 |
| PQC 算法黑名單測試 | Client / MITM | 中 |
| Kyber/ML-KEM 錯誤封裝攻擊 | Client / MITM | 高 |
| Dilithium/ML-DSA 簽章驗證繞過 | Client / MITM | 高 |
| PQC 憑證鏈深度攻擊 | Server / MITM | 中 |
| 格攻擊參數探測 | Passive / Client | 高 |
| PQC 隨機數品質測試 | Passive | 高 |

### B. 側信道與時序攻擊

| 攻擊手法 | 發起位置 | 難度 |
|---------|---------|------|
| KEM Decapsulation 時序攻擊 | Client / Passive | 高 |
| 簽章驗證時序側信道 | Client / Passive | 高 |
| Cache-timing 攻擊 | Local / Passive | 高 |
| 連線建立時間指紋 | Passive | 低 |
| 封包大小指紋 | Passive | 低 |

### C. 憑證與身份攻擊

| 攻擊手法 | 發起位置 | 難度 |
|---------|---------|------|
| PQC 憑證替換攻擊 | MITM | 高 |
| 跨算法憑證混淆 | MITM | 中 |
| 憑證透明度日誌偽造 | MITM | 高 |
| OCSP stapling 剝除 | MITM | 低 |
| CRL 投毒攻擊 | Network | 中 |
| 憑證驗證錯誤 (unknown_ca / expired / name mismatch) | Server / MITM | 低 |

### D. 協議邏輯攻擊

| 攻擊手法 | 發起位置 | 難度 |
|---------|---------|------|
| Early Data / 0-RTT 重放 | Client / MITM | 中 |
| 0-RTT 接受／拒絕差異觀察 | Passive / MITM | 低 |
| Post-Handshake 認證濫用 | Client / Server | 中 |
| KeyUpdate 洪水攻擊 | Client / Server | 中 |
| NewSessionTicket 洪泛 | Server | 低 |
| HelloRetryRequest 觸發濫用 | Client / MITM | 中 |
| PSK／Session Ticket 失效導致回退 | Client / MITM | 中 |

### E. 實作漏洞探測

| 攻擊手法 | 發起位置 | 難度 |
|---------|---------|------|
| 整數溢位測試 | Client / MITM | 中 |
| 緩衝區溢位（PQC 大數據） | Client / Server | 高 |
| 格式化字串漏洞 | Client / MITM | 中 |
| NULL pointer dereference | Client / Server | 中 |
| 資源洩漏測試 | Client | 中 |
| 大型 ClientHello 不相容（GREASE／擴展膨脹） | Client | 中 |

### F. 混合模式特定攻擊

| 攻擊手法 | 發起位置 | 難度 |
|---------|---------|------|
| 混合 KEM 部分失效攻擊 | MITM | 高 |
| 混合簽章不一致攻擊 | MITM | 高 |
| 算法優先級操縱 | MITM | 中 |
| 協商回退（NamedGroup 回落） | MITM | 中 |

### G. DoS 與資源耗盡

| 攻擊手法 | 發起位置 | 難度 |
|---------|---------|------|
| 握手洪泛（短連線高併發） | Client | 低 |
| KEM 計算耗竭（Decapsulation 峰值） | Client | 中 |
| 慢速 Handshake 攻擊 | Client | 低 |
| Certificate Chain 放大 | Server | 中 |
| Extension 爆炸攻擊 | Client | 低 |
| 並行連線耗盡 | Client | 低 |

### H. 降級與相容性攻擊

| 攻擊手法 | 發起位置 | 難度 |
|---------|---------|------|
| TLS 版本降級 | MITM | 中 |
| 密碼套件降級 | MITM | 中 |
| ALPN 協商干擾 | MITM | 低 |
| SNI／ALPN 阻擋導致握手失敗 | MITM | 低 |
| 路徑版本／群組不容忍 | MITM | 中 |

### I. 流量分析與指紋

| 攻擊手法 | 發起位置 | 難度 |
|---------|---------|------|
| TLS 指紋識別（JA3/JA4） | Passive | 低 |
| PQC 算法指紋 | Passive | 低 |
| 網站指紋攻擊 | Passive | 中 |
| 流量相關性分析 | Passive | 中 |
| 應用行為推測 | Passive | 中 |

### J. 網路層攻擊

| 攻擊手法 | 發起位置 | 難度 |
|---------|---------|------|
| 網路劣化（丟包／延遲／抖動） | MITM | 低 |
| MTU／MSS 限制（握手分段／黑洞） | MITM / Network | 中 |
| TCP 重排／突發丟失／RST 注入 | MITM | 中 |
| TLS Alert 注入 | MITM / Client / Server | 中 |
| 中間盒／代理阻擋新群組或未知擴展 | MITM | 中 |

### K. QUIC 相關攻擊（如適用）

| 攻擊手法 | 發起位置 | 難度 |
|---------|---------|------|
| QUIC 初始封包遺失 | MITM | 中 |
| QUIC Retry 要求濫用 | Server / MITM | 中 |
| QUIC 0-RTT 封包拒絕／丟棄觀察 | Server / MITM | 中 |
| QUIC 流量整形／速率限制 | MITM | 中 |

### L. 新興威脅

| 攻擊手法 | 發起位置 | 難度 |
|---------|---------|------|
| Store Now, Decrypt Later | Passive | 低 |
| ML/AI 輔助攻擊 | Passive / MITM | 高 |
| 區塊鏈時間戳偽造 | MITM | 中 |
| DNS-over-HTTPS 繞過 | Network | 中 |

---

## 📦 封包結構分析

### TLS 封包層級比較

| 層級 | 欄位 | 傳統 TLS | PQC-TLS | 相同？ |
|------|------|----------|---------|--------|
| **Layer 2-4** | 所有欄位 | 標準 | 標準 | ✅ 完全相同 |
| **TLS Record** | Content Type, Version | 標準 | 標準 | ✅ 相同 |
| **TLS Record** | Length | ~300 bytes | ~1500-2000 bytes | ⚠️ 值不同 |
| **Extension** | supported_groups | x25519, secp256r1 | kyber768, dilithium3 | ❌ 值不同 |
| **Extension** | key_share | 32 bytes | 1184 bytes | ❌ 大小差異大 |
| **Certificate** | 總大小 | ~1-2 KB | ~5-10 KB | ❌ 大小差異大 |

### Extension 和 Data Size 差異原因

**原因：PQC 算法的數學特性**

#### 密鑰大小對比

| 算法類型 | 算法名稱 | 公鑰大小 | 密文/簽章大小 | 倍數 |
|---------|---------|---------|--------------|------|
| **傳統 ECDH** | x25519 | 32 bytes | - | 1x |
| **傳統 ECDSA** | secp256r1 | 65 bytes | ~72 bytes | 1x |
| **PQC KEM** | Kyber512 | 800 bytes | 768 bytes | **25x** |
| **PQC KEM** | Kyber768 | 1184 bytes | 1088 bytes | **37x** |
| **PQC KEM** | Kyber1024 | 1568 bytes | 1568 bytes | **49x** |
| **PQC 簽章** | Dilithium2 | 1312 bytes | 2420 bytes | **20x** |
| **PQC 簽章** | Dilithium3 | 1952 bytes | 3293 bytes | **33x** |
| **PQC 簽章** | Falcon512 | 897 bytes | 666 bytes | **10x** |

#### 握手階段封包大小

```
                    傳統 TLS 1.3    PQC-TLS 1.3
─────────────────────────────────────────────────
ClientHello         ~300 bytes      ~1500-2000 bytes  (5-7x)
ServerHello         ~150 bytes      ~1300 bytes       (8-9x)
Certificate         ~1500 bytes     ~6000-8000 bytes  (4-5x)
CertificateVerify   ~100 bytes      ~2500 bytes       (25x)
Finished            ~50 bytes       ~50 bytes         (相同)

總握手大小         ~2100 bytes     ~12000-14000 bytes (6-7x)
```

---

## 開發環境設定

### 步驟 1：安裝 liboqs

```bash
# Clone liboqs
cd ~
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs

# 編譯安裝
mkdir build && cd build
cmake -GNinja -DCMAKE_INSTALL_PREFIX=/usr/local ..
ninja
sudo ninja install

# 更新動態庫路徑
sudo ldconfig
```

### 步驟 4：建立專案並安裝 Python 套件

```bash
# 建立專案目錄
cd ~
mkdir pqc-tls-research
cd pqc-tls-research

# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝 Python 套件
pip install --upgrade pip

# 核心套件
pip install liboqs-python      # PQC 密碼學
pip install scapy              # 封包操作
pip install mitmproxy          # MITM 框架
pip install cryptography       # 密碼學工具
pip install pyOpenSSL          # OpenSSL 綁定

# 分析工具
pip install pandas numpy matplotlib
pip install pyyaml

# 網路工具
pip install requests aiohttp
```

### requirements.txt

```txt
liboqs-python>=0.8.0
scapy>=2.5.0
mitmproxy>=10.0.0
cryptography>=41.0.0
pyOpenSSL>=23.0.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
pyyaml>=6.0
requests>=2.31.0
aiohttp>=3.8.0
```

### 步驟 5：驗證安裝

```bash
# 測試 liboqs
python3 << EOF
import oqs
print("支援的 KEM 算法:")
for kem in oqs.get_enabled_KEM_mechanisms():
    print(f"  - {kem}")
print("\n支援的簽章算法:")
for sig in oqs.get_enabled_sig_mechanisms():
    print(f"  - {sig}")
EOF
```

---

## 🛠️ 開發工具

### VS Code 配置

#### 安裝擴展
```
必裝擴展：
- Python (Microsoft)
- Pylance
- Remote - WSL
- GitLens

選用擴展：
- Jupyter
- YAML
- Better Comments
```

#### 連接到 WSL
```
1. 按 F1
2. 輸入 "WSL: Connect to WSL"
3. 選擇 Ubuntu
4. 開啟專案資料夾: ~/pqc-tls-research
```

---

## 📁 專案結構

```
pqc-tls-research/
├── README.md
├── requirements.txt
├── .gitignore
│
├── core/                          # 核心系統
│   ├── __init__.py
│   ├── normal_client.py           # 正常客戶端
│   ├── normal_server.py           # 正常伺服器
│   ├── malicious_client.py        # 惡意客戶端 (Client 端攻擊)
│   ├── malicious_server.py        # 惡意伺服器 (Server 端攻擊)
│   ├── mitm_proxy.py              # MITM 代理 (中間人攻擊)
│   └── passive_monitor.py         # 被動監聽 (被動分析)
│
├── attacks/                       # 攻擊模組
│   ├── __init__.py
│   │
│   ├── pqc_specific/              # PQC 特定攻擊 (8 個)
│   │   ├── __init__.py
│   │   ├── key_size_amplification.py
│   │   ├── hybrid_downgrade.py
│   │   ├── kyber_malformed.py
│   │   ├── dilithium_bypass.py
│   │   └── ...
│   │
│   ├── sidechannel/               # 側信道攻擊 (7 個)
│   │   ├── __init__.py
│   │   ├── timing_attack.py
│   │   ├── signature_timing.py
│   │   └── ...
│   │
│   ├── certificate/               # 憑證攻擊 (6 個)
│   │   ├── __init__.py
│   │   ├── cert_replacement.py
│   │   ├── ocsp_stripping.py
│   │   └── ...
│   │
│   ├── protocol_logic/            # 協議邏輯攻擊 (7 個)
│   │   ├── __init__.py
│   │   ├── zero_rtt_replay.py
│   │   ├── hello_retry_abuse.py
│   │   └── ...
│   │
│   ├── implementation/            # 實作漏洞 (7 個)
│   │   ├── __init__.py
│   │   ├── buffer_overflow.py
│   │   ├── integer_overflow.py
│   │   └── ...
│   │
│   ├── hybrid_mode/               # 混合模式攻擊 (4 個)
│   │   ├── __init__.py
│   │   ├── partial_failure.py
│   │   └── ...
│   │
│   ├── dos/                       # DoS 攻擊 (6 個)
│   │   ├── __init__.py
│   │   ├── handshake_flood.py
│   │   ├── kem_exhaustion.py
│   │   └── ...
│   │
│   ├── downgrade/                 # 降級攻擊 (5 個)
│   │   ├── __init__.py
│   │   ├── version_downgrade.py
│   │   ├── cipher_downgrade.py
│   │   └── ...
│   │
│   ├── traffic_analysis/          # 流量分析 (5 個)
│   │   ├── __init__.py
│   │   ├── ja3_fingerprint.py
│   │   ├── pqc_fingerprint.py
│   │   └── ...
│   │
│   └── network/                   # 網路層攻擊 (20+ 個)
│       ├── __init__.py
│       ├── packet_loss.py
│       ├── delay_injection.py
│       ├── tcp_rst_injection.py
│       └── ...
│
├── utils/                         # 工具函數
│   ├── __init__.py
│   ├── packet_parser.py           # 封包解析
│   ├── traffic_capture.py         # 流量捕獲
│   ├── crypto_utils.py            # 密碼學工具
│   ├── logger.py                  # 日誌記錄
│   └── config_loader.py           # 配置載入
│
├── experiments/                   # 實驗腳本
│   ├── run_dos_test.py
│   ├── run_downgrade_test.py
│   ├── run_timing_analysis.py
│   └── analyze_results.py
│
├── configs/                       # 配置文件
│   ├── attack_config.yaml
│   ├── server_config.yaml
│   └── client_config.yaml
│
├── data/                          # 數據和結果
│   ├── pcaps/                    # 封包捕獲文件
│   ├── logs/                     # 日誌文件
│   └── results/                  # 實驗結果
│
├── docs/                          # 文檔
│   ├── attack_descriptions.md
│   ├── setup_guide.md
│   └── api_reference.md
│
└── notebooks/                     # Jupyter Notebooks (可選)
    ├── data_analysis.ipynb
    └── visualization.ipynb
```

---

## 🔧 可用工具和資源

### 直接可用的工具（~40% 攻擊）

| 工具 | 涵蓋的攻擊類型 | 安裝方式 |
|------|--------------|---------|
| **mitmproxy** | MITM 基礎、協議操縱 | `pip install mitmproxy` |
| **Scapy** | 封包操作、注入 | `pip install scapy` |
| **tc/netem** | 網路劣化 | Linux 內建 |
| **hping3** | DoS 測試 | `sudo apt install hping3` |
| **Wireshark** | 流量分析 | `sudo apt install wireshark` |
| **testssl.sh** | 協議測試 | `git clone https://github.com/drwetter/testssl.sh` |

### 需自行開發（~60% 攻擊）

以下攻擊需要自行實作：
- 所有 PQC 特定攻擊（8 種）
- 大部分混合模式攻擊（4 種）
- 部分側信道攻擊（4-5 種）
- 部分實作漏洞探測（5-6 種）

---

## 📊 研究階段規劃

### Phase 1: 環境建設（1-2 週）
- [ ] 安裝 WSL2 和開發環境
- [ ] 編譯 liboqs
- [ ] 安裝 Python 套件
- [ ] 驗證環境正常運作
- [ ] 建立專案結構

### Phase 2: 基礎設施（2-3 週）
- [ ] 實作 `normal_client.py`
- [ ] 實作 `normal_server.py`
- [ ] 實作基本流量捕獲
- [ ] 實作封包解析工具
- [ ] 測試正常 PQC-TLS 連接

### Phase 3: 攻擊工具開發（3-4 週）
- [ ] 實作 `malicious_client.py`
- [ ] 實作 `malicious_server.py`
- [ ] 實作 `mitm_proxy.py`
- [ ] 實作 `passive_monitor.py`

### Phase 4: PQC 特定攻擊（3-4 週）
- [ ] PQC 密鑰尺寸放大攻擊
- [ ] 混合模式降級攻擊
- [ ] Kyber 錯誤封裝攻擊
- [ ] Dilithium 簽章繞過測試
- [ ] 其他 PQC 特定攻擊

### Phase 5: 被動攻擊（2-3 週）
- [ ] 時序攻擊
- [ ] 流量分析
- [ ] 側信道分析
- [ ] 指紋識別

### Phase 6: 主動攻擊（3-4 週）
- [ ] MITM 降級攻擊
- [ ] 協議操縱攻擊
- [ ] 重放攻擊
- [ ] 注入攻擊

### Phase 7: DoS 和壓力測試（2 週）
- [ ] 握手洪泛
- [ ] KEM 計算耗竭
- [ ] 資源消耗測試

### Phase 8: 數據分析和報告（2-3 週）
- [ ] 數據收集和整理
- [ ] 效能分析
- [ ] 安全性評估
- [ ] 撰寫研究報告

**總計：約 18-25 週（4-6 個月）**

---

## 🎓 學習資源

### 官方文檔
- **Open Quantum Safe**: https://openquantumsafe.org/
- **liboqs Documentation**: https://github.com/open-quantum-safe/liboqs/wiki
- **NIST PQC Project**: https://csrc.nist.gov/projects/post-quantum-cryptography

### 工具文檔
- **mitmproxy**: https://docs.mitmproxy.org/
- **Scapy**: https://scapy.readthedocs.io/
- **TLS-Attacker**: https://github.com/tls-attacker/TLS-Attacker/wiki

### 研究論文
- "Post-Quantum TLS without Handshake Signatures" (Google)
- "Hybrid Key Exchange in TLS 1.3" (IETF Draft)
- "Side-Channel Analysis of Lattice-Based Post-Quantum Cryptography"

---

## ⚠️ 研究倫理與法律

**重要提醒**：
1. ✅ **只在受控環境測試**（自己的網路和設備）
2. ✅ **不要針對真實系統**
3. ✅ **遵守學術倫理規範**
4. ✅ **取得必要的批准**（學校 IRB 等）
5. ✅ **負責任地披露發現的漏洞**

---

## 📈 預期產出

### 技術產出
1. **開源工具**：完整的 PQC-TLS 攻擊測試框架
2. **攻擊資料庫**：79+ 種攻擊的實作和分析
3. **測試數據集**：封包捕獲、效能數據、漏洞報告

### 學術產出
1. **研究論文**：投稿國際會議或期刊
2. **技術報告**：詳細的攻擊實作和結果分析
3. **安全建議**：給 PQC-TLS 實作者和標準化組織的建議

### 教育產出
1. **教學材料**：PQC-TLS 安全性教學資源
2. **Demo 和 Presentation**：研究成果展示

---

## 🚀 快速開始

```bash
# 1. 安裝 WSL2
wsl --install -d Ubuntu-22.04

# 2. 進入 WSL 並執行安裝腳本
wsl
git clone <your-repo-url> pqc-tls-research
cd pqc-tls-research
bash setup.sh

# 3. 啟動虛擬環境
source venv/bin/activate

# 4. 執行測試
python3 demo_pqc.py

# 5. 開始開發！
code .
```

---

## 📞 聯絡資訊

如有問題或需要協助，請：
- 查閱文檔：`docs/`
- 提交 Issue
- 查看 FAQ

---

## 📝 版本歷史

- **v1.0** (2025-11): 初始專案規劃
  - 定義 79+ 種攻擊手法
  - 建立核心架構
  - 完成環境設定指南

---

## 🌊 流量模擬系統

### 目標

將真實世界流量特徵轉換為基於 PQC-TLS 的正常流量資料集。

### 架構
```
真實流量來源 (PCAP/JSON)
    ↓
來源管理器 (source_manager)
    ↓
模擬引擎 (traffic_simulator)
    ↓
執行層 (simulation_client/server)
    ↓
捕獲層 (dataset_builder → traffic_capture)
    ↓
PQC-TLS 資料集 (PCAP + metadata)
    ↓
分析器 (analyzer)
```

### 核心模組

| 模組 | 路徑 | 職責 |
|------|------|------|
| 來源管理 | `simulate_base/source_manager.py` | 讀取並統一流量特徵 |
| 模擬引擎 | `simulate_base/traffic_simulator.py` | 調度連線和時序控制 |
| Client 包裝 | `simulate_base/simulation_client.py` | 包裝 normal_client |
| Server 包裝 | `simulate_base/simulation_server.py` | 包裝 normal_server |
| 資料集建構 | `simulate_base/dataset_builder.py` | 捕獲並組織資料集 |
| 分析器 | `simulate_base/analyzer.py` | 事後分析和報告 |

### 與核心系統的關聯
```
模擬系統使用核心系統的：
- core/normal_client.py（被包裝）
- core/normal_server.py（被包裝）
- utils/traffic_capture.py（被整合）
- utils/settings.py（共用配置）

核心系統不依賴模擬系統（單向依賴）
```

### 配置管理

- **全域配置**: `serversetting.yaml`（OpenSSL、PQC 算法）
- **模擬配置**: `simulate_base/simulation_config.yaml`（模擬參數）

### 詳細文檔

- 總覽：`simulate_base/README.md`
- 實作計劃：`simulate_base/IMPLEMENTATION_PLAN.md`
- API 參考：`simulate_base/API_REFERENCE.md`


## 📄 授權

本專案僅供學術研究和教育用途。請遵守相關法律法規和倫理規範。

---

**最後更新**：2025-11-02
**文件版本**：1.0
