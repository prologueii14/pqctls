# API 參考文檔

## `source_manager.py`

### SourceManager

**職責**: 管理流量來源，提供統一介面

#### 初始化
```python
from source_manager import SourceManager

mgr = SourceManager(config)
```

#### 方法

##### `get_features() -> dict`
```python
features = mgr.get_features()
# 回傳:
# {
#   'packet_sizes': [100, 1500, ...],
#   'intervals': [0.01, 0.05, ...],
#   'protocols': ['TCP', 'TCP', ...]
# }
```

##### `get_connection_pattern() -> dict`
```python
pattern = mgr.get_connection_pattern()
# 回傳:
# {
#   'short': 0.7,  # 70% 短連線
#   'long': 0.3    # 30% 長連線
# }
```

---

## `traffic_simulator.py`

### TrafficSimulator

**職責**: 核心模擬引擎

#### 初始化
```python
from traffic_simulator import TrafficSimulator

simulator = TrafficSimulator(config)
```

#### 方法

##### `setup()`
啟動 Server，建立 Client 池

##### `run()`
執行模擬（阻塞）

##### `stop()`
停止並清理

---

## `dataset_builder.py`

### DatasetBuilder

**職責**: 捕獲並組織資料集

#### 初始化
```python
from dataset_builder import DatasetBuilder

builder = DatasetBuilder(config)
```

#### 方法

##### `start_capture()`
開始捕獲（背景執行緒）

##### `stop_and_save() -> str`
停止並儲存，回傳輸出目錄

---

## `analyzer.py`

### DatasetAnalyzer

**職責**: 分析資料集

#### 方法

##### `analyze(dataset_dir: str) -> dict`
分析資料集，回傳報告

##### `generate_report(output_file: str)`
產生文字報告

---

## 配置格式

### `simulation_config.yaml`
```yaml
# 模擬參數
simulation:
  mode: "statistical"      # 模式
  duration: 30             # 持續時間（秒）
  
  execution:
    threading: true        # 多執行緒
    async: false           # 非同步
    max_workers: 10        # 最大執行緒

# 來源
sources:
  - type: "json"
    path: "features/xxx.json"
    weight: 1.0

# 拓樸
topology:
  clients: 5
  server_port: 8443
  connection_pattern: "realistic"
  
  per_client:
    connections: 10
    interval_range: [0.1, 2.0]

# 輸出
dataset:
  output_dir: "datasets"
  format: "pcap"
  
  metadata:
    label: "normal"
    scenario: "web_browsing"
```