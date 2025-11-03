# PQC-TLS 研究環境配置文檔

**最後更新**: 2025-11-02
**環境版本**: v1.0

---

## 📋 目錄

1. [環境概述](#環境概述)
2. [已安裝組件](#已安裝組件)
3. [目錄結構](#目錄結構)
4. [重要路徑](#重要路徑)
5. [完整重建步驟](#完整重建步驟)
6. [環境驗證](#環境驗證)
7. [故障排除](#故障排除)

---

## 🎯 環境概述

### 作業系統
- **OS**: Windows 11
- **開發環境**: Anaconda (yolov11 環境)
- **Python 版本**: 3.x

### 核心組件版本
| 組件 | 版本 | 用途 |
|------|------|------|
| liboqs | 0.14.0 | PQC 密碼學庫 |
| oqs-provider | 0.10.0 | OpenSSL PQC provider |
| OpenSSL | 3.3.2 | TLS 協議實作 |
| liboqs-python | 0.14.1 | Python 綁定 |
| Scapy | 2.5.0+ | 封包操作 |
| Npcap | latest | 封包捕獲 |

---

## 📦 已安裝組件

### 1. liboqs (編譯版)
- **位置**: `H:\Workspace\NYCU\Code\pqctls\liboqs`
- **編譯產物**: `H:\Workspace\NYCU\Code\pqctls\liboqs\dist`
- **重要檔案**:
  - `dist/bin/liboqs.dll` (動態庫)
  - `dist/lib/liboqs.a` (靜態庫)
  - `dist/include/oqs/*` (標頭檔)

### 2. oqs-provider (編譯版)
- **位置**: `H:\Workspace\NYCU\Code\pqctls\oqs-provider-0.10.0`
- **編譯產物**: `H:\Workspace\NYCU\Code\pqctls\oqs-provider-0.10.0\build\lib`
- **重要檔案**:
  - `build/lib/oqsprovider.dll` (OpenSSL provider)

### 3. OpenSSL (Anaconda 版)
- **位置**: `C:\Users\88692\anaconda3\envs\yolov11\Library`
- **執行檔**: `C:\Users\88692\anaconda3\envs\yolov11\Library\bin\openssl.exe`
- **版本**: 3.3.2

### 4. Python 套件
```bash
liboqs-python==0.14.1
scapy>=2.5.0
cryptography>=41.0.0
pyOpenSSL>=23.0.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
pyyaml>=6.0
requests>=2.31.0
aiohttp>=3.8.0
```

---

## 📁 目錄結構
```
H:\Workspace\NYCU\Code\pqctls\
├── liboqs/                              # liboqs 原始碼
│   ├── build/                           # 編譯目錄
│   └── dist/                            # 安裝目錄 ⭐
│       ├── bin/liboqs.dll               # 主要 DLL
│       ├── lib/                         # 庫檔案
│       └── include/oqs/                 # 標頭檔
│
├── oqs-provider-0.10.0/                 # oqs-provider 原始碼
│   └── build/                           # 編譯目錄
│       └── lib/oqsprovider.dll          # Provider DLL ⭐
│
├── test/                                # 測試腳本
│   ├── test_env.py
│   └── test_oqs_provider.py
│
└── core/                                # 主要程式碼（待建立）
    ├── normal_client.py
    └── normal_server.py
```

---

## 🔑 重要路徑

### 環境變數配置
```python
# 需要設定的環境變數
os.environ['OQS_INSTALL_PATH'] = r'H:\Workspace\NYCU\Code\pqctls\liboqs\dist'
os.environ['PATH'] = r'H:\Workspace\NYCU\Code\pqctls\liboqs\dist\bin;' + os.environ['PATH']
os.environ['OPENSSL_MODULES'] = r'H:\Workspace\NYCU\Code\pqctls\oqs-provider-0.10.0\build\lib'
```

### OpenSSL 指令範例
```bash
# 使用 PQC 的 OpenSSL 指令格式
openssl list -providers -provider-path "H:\Workspace\NYCU\Code\pqctls\oqs-provider-0.10.0\build\lib" -provider oqsprovider
```

---

## 🔨 完整重建步驟

### 前置需求

#### 1. 安裝系統工具
```bash
# 需要的工具（透過 Chocolatey 或手動安裝）
- CMake (https://cmake.org/download/)
- Ninja (https://github.com/ninja-build/ninja/releases)
- GCC/MinGW (https://www.mingw-w64.org/)
- Git (https://git-scm.com/downloads)
```

#### 2. 安裝 Anaconda
```bash
# 下載並安裝 Anaconda
# 網址: https://www.anaconda.com/download

# 建立環境
conda create -n pqc-tls python=3.10
conda activate pqc-tls
```

#### 3. 安裝 Npcap
```bash
# 下載: https://npcap.com/#download
# 安裝時勾選:
# ✅ Install Npcap in WinPcap API-compatible Mode
# ✅ Support raw 802.11 traffic
```

---

### 步驟 1: 編譯 liboqs
```bash
# 1.1 Clone liboqs
cd H:\Workspace\NYCU\Code\pqctls
git clone --branch 0.14.0 https://github.com/open-quantum-safe/liboqs.git
cd liboqs

# 1.2 建立 build 目錄
mkdir build
cd build

# 1.3 配置 CMake (編譯 shared library)
cmake -GNinja -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON -DBUILD_TESTING=OFF ..

# 1.4 編譯
cmake --build . --config Release

# 1.5 安裝到 dist 目錄
cmake --install . --config Release --prefix "..\dist"

# 1.6 驗證
dir ..\dist\bin\liboqs.dll
```

**預期結果**: 看到 `liboqs.dll` 檔案

---

### 步驟 2: 安裝 Python 套件
```bash
# 2.1 確保在正確的 Anaconda 環境
conda activate pqc-tls

# 2.2 安裝套件
pip install --upgrade pip
pip install liboqs-python==0.14.1
pip install scapy cryptography pyOpenSSL
pip install pandas numpy matplotlib pyyaml requests aiohttp

# 2.3 驗證 liboqs-python
python -c "import oqs; print('liboqs-python OK')"
```

---

### 步驟 3: 編譯 oqs-provider
```bash
# 3.1 下載 oqs-provider
cd H:\Workspace\NYCU\Code\pqctls
# 從 https://github.com/open-quantum-safe/oqs-provider/releases
# 下載 Source code (zip) 並解壓為 oqs-provider-0.10.0

# 3.2 建立 build 目錄
cd oqs-provider-0.10.0
mkdir build
cd build

# 3.3 配置 CMake（⚠️ 替換路徑為你的實際路徑）
cmake -GNinja ^
  -DCMAKE_BUILD_TYPE=Release ^
  -DOPENSSL_ROOT_DIR="C:\Users\YOUR_USERNAME\anaconda3\envs\pqc-tls\Library" ^
  -DOPENSSL_INCLUDE_DIR="C:\Users\YOUR_USERNAME\anaconda3\envs\pqc-tls\Library\include" ^
  -DOPENSSL_CRYPTO_LIBRARY="C:\Users\YOUR_USERNAME\anaconda3\envs\pqc-tls\Library\lib\libcrypto.lib" ^
  -DOPENSSL_SSL_LIBRARY="C:\Users\YOUR_USERNAME\anaconda3\envs\pqc-tls\Library\lib\libssl.lib" ^
  -Dliboqs_DIR="H:\Workspace\NYCU\Code\pqctls\liboqs\dist\lib\cmake\liboqs" ^
  -DOQS_PROVIDER_BUILD_STATIC=OFF ^
  ..

# 3.4 編譯（只編譯 provider，跳過測試）
cmake --build . --target oqsprovider

# 3.5 驗證
dir lib\oqsprovider.dll
```

**預期結果**: 看到 `oqsprovider.dll` 檔案

---

### 步驟 4: 環境驗證

建立並執行驗證腳本 `verify_environment.py`:
```python
import os
import sys
import subprocess

print("=" * 70)
print("PQC-TLS 環境完整驗證")
print("=" * 70)

# 設定路徑（⚠️ 根據實際情況修改）
BASE_PATH = r"H:\Workspace\NYCU\Code\pqctls"
CONDA_ENV = r"C:\Users\88692\anaconda3\envs\pqc-tls"

PATHS = {
    'liboqs_dll': os.path.join(BASE_PATH, 'liboqs', 'dist', 'bin', 'liboqs.dll'),
    'oqs_provider': os.path.join(BASE_PATH, 'oqs-provider-0.10.0', 'build', 'lib', 'oqsprovider.dll'),
    'openssl': os.path.join(CONDA_ENV, 'Library', 'bin', 'openssl.exe'),
}

def check_files():
    print("\n[1] 檢查檔案存在...")
    all_ok = True
    for name, path in PATHS.items():
        if os.path.exists(path):
            print(f"  ✅ {name}: {path}")
        else:
            print(f"  ❌ {name}: {path} (不存在)")
            all_ok = False
    return all_ok

def check_liboqs_python():
    print("\n[2] 檢查 liboqs-python...")
    try:
        import oqs
        kem = oqs.KeyEncapsulation("Kyber512")
        print("  ✅ liboqs-python 可用")
        return True
    except Exception as e:
        print(f"  ❌ liboqs-python 錯誤: {e}")
        return False

def check_scapy():
    print("\n[3] 檢查 Scapy...")
    try:
        from scapy.all import conf
        if conf.use_pcap:
            print("  ✅ Scapy + Npcap 可用")
        else:
            print("  ⚠️  Scapy 可用但缺少 Npcap")
        return True
    except Exception as e:
        print(f"  ❌ Scapy 錯誤: {e}")
        return False

def check_oqs_provider():
    print("\n[4] 檢查 oqs-provider...")
    
    # 設定環境變數
    os.environ['PATH'] = f"{os.path.dirname(PATHS['liboqs_dll'])};{os.path.dirname(PATHS['openssl'])};{os.environ.get('PATH', '')}"
    
    cmd = [
        PATHS['openssl'], 
        'list', '-providers',
        '-provider-path', os.path.dirname(PATHS['oqs_provider']),
        '-provider', 'oqsprovider'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if 'oqsprovider' in result.stdout.lower():
            print("  ✅ oqs-provider 可用")
            return True
        else:
            print("  ❌ oqs-provider 未載入")
            print(f"  輸出: {result.stdout}")
            print(f"  錯誤: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ 執行錯誤: {e}")
        return False

def main():
    results = []
    results.append(check_files())
    results.append(check_liboqs_python())
    results.append(check_scapy())
    results.append(check_oqs_provider())
    
    print("\n" + "=" * 70)
    if all(results):
        print("✅ 所有檢查通過！環境建立成功！")
    else:
        print("❌ 部分檢查失敗，請檢查上述錯誤訊息")
    print("=" * 70)

if __name__ == "__main__":
    main()
```

執行驗證:
```bash
python verify_environment.py
```

**預期輸出**: 所有項目顯示 ✅

---

## ✅ 環境驗證檢查表

完成以下所有項目代表環境建立成功：

- [ ] liboqs.dll 存在且可載入
- [ ] oqsprovider.dll 存在且可載入
- [ ] liboqs-python 可以建立 Kyber512 實例
- [ ] OpenSSL 可以載入 oqs-provider
- [ ] OpenSSL 可以列出 PQC 算法（kyber, dilithium 等）
- [ ] Scapy 可以運作
- [ ] Npcap 已安裝

---

## 🔧 故障排除

### 問題 1: 找不到 liboqs.dll
**症狀**: `RuntimeError: No oqs shared libraries found`

**解決方案**:
```python
# 設定環境變數
os.environ['OQS_INSTALL_PATH'] = r'H:\Workspace\NYCU\Code\pqctls\liboqs\dist'
os.environ['PATH'] = r'H:\Workspace\NYCU\Code\pqctls\liboqs\dist\bin;' + os.environ['PATH']
```

### 問題 2: OpenSSL 找不到 oqs-provider
**症狀**: `openssl list -providers` 沒有顯示 oqsprovider

**解決方案**:
```bash
# 必須指定 -provider-path 和 -provider
openssl list -providers \
  -provider-path "H:\Workspace\NYCU\Code\pqctls\oqs-provider-0.10.0\build\lib" \
  -provider oqsprovider
```

### 問題 3: CMake 找不到 OpenSSL
**症狀**: `Could NOT find OpenSSL`

**解決方案**:
```bash
# 使用完整路徑指定 OpenSSL
# 檢查 OpenSSL 位置
where openssl

# 使用該路徑的 Library 目錄
-DOPENSSL_ROOT_DIR="C:\Users\YOUR_USERNAME\anaconda3\envs\pqc-tls\Library"
```

### 問題 4: 編譯 oqs-provider 測試失敗
**症狀**: `mkdir` 參數錯誤

**解決方案**:
```bash
# 跳過測試，只編譯 provider
cmake --build . --target oqsprovider
```

### 問題 5: Scapy 缺少 libpcap
**症狀**: `WARNING: No libpcap provider available`

**解決方案**:
1. 下載安裝 Npcap: https://npcap.com/#download
2. 安裝時勾選 "WinPcap API-compatible Mode"

---

## 📦 環境備份與遷移

### 備份編譯產物
```bash
# 備份重要檔案
mkdir H:\Workspace\NYCU\Code\pqctls\backup

# 備份 liboqs
xcopy H:\Workspace\NYCU\Code\pqctls\liboqs\dist H:\Workspace\NYCU\Code\pqctls\backup\liboqs /E /I

# 備份 oqs-provider
xcopy H:\Workspace\NYCU\Code\pqctls\oqs-provider-0.10.0\build\lib H:\Workspace\NYCU\Code\pqctls\backup\oqs-provider /E /I
```

### 遷移到新環境
1. 複製整個 `pqctls` 目錄到新位置
2. 修改所有腳本中的路徑
3. 重新執行環境驗證腳本

### 關鍵檔案清單（可直接複製）
```
必須複製的檔案:
├── liboqs/dist/bin/liboqs.dll
├── liboqs/dist/lib/liboqs.a
├── liboqs/dist/include/oqs/*
└── oqs-provider-0.10.0/build/lib/oqsprovider.dll
```

---

## 📞 支援資源

- **liboqs 文檔**: https://github.com/open-quantum-safe/liboqs/wiki
- **oqs-provider 文檔**: https://github.com/open-quantum-safe/oqs-provider
- **OpenSSL 文檔**: https://www.openssl.org/docs/
- **NIST PQC**: https://csrc.nist.gov/projects/post-quantum-cryptography

---

## 📝 變更日誌

### v1.0 (2025-11-02)
- 初始環境建立
- liboqs 0.14.0 編譯成功
- oqs-provider 0.10.0 編譯成功
- 所有測試通過

---

**文檔結束**