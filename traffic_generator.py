import yaml
import importlib
import threading
import time
from pathlib import Path
from datetime import datetime
from core.normal_server import TLSServer
from utils.traffic_capture import TrafficCapture

# python traffic_generator.py configs/experiments/exp_01_benign.yaml
# python traffic_generator.py configs/experiments/exp_00_quick_test.yaml
class TrafficGenerator:
    def __init__(self, patterns_file='configs/traffic_patterns.yaml'):
        self.patterns_file = patterns_file
        self.patterns = self.load_patterns()
        self.server = None
        self.server_thread = None
        self.capture = None

        self.attack_classes = {
            'web_browsing': 'attacks.benign.simple_traffic.SimpleTraffic',
            'video_streaming': 'attacks.benign.simple_traffic.SimpleTraffic',
            'file_download': 'attacks.benign.simple_traffic.SimpleTraffic',
            'gaming': 'attacks.benign.simple_traffic.SimpleTraffic',
        }

    def load_patterns(self):
        patterns_path = Path(self.patterns_file)
        if not patterns_path.exists():
            raise FileNotFoundError(f"找不到配置檔案: {self.patterns_file}")

        with open(patterns_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return data

    def load_attack_class(self, pattern_name):
        if pattern_name not in self.attack_classes:
            raise ValueError(f"未定義攻擊類別: {pattern_name}")

        class_path = self.attack_classes[pattern_name]
        module_path, class_name = class_path.rsplit('.', 1)

        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    def start_server(self):
        server_config = self.patterns.get('server', {})
        port = server_config.get('port', 4433)
        kem_algorithm = server_config.get('kem_algorithm', 'mlkem768')
        sig_algorithm = server_config.get('sig_algorithm', 'mldsa65')
        keylog_file = server_config.get('keylog_file', None)

        print(f"\n啟動 PQC-TLS Server...")
        print(f"  Port: {port}")
        print(f"  KEM: {kem_algorithm}")
        print(f"  Signature: {sig_algorithm}")
        if keylog_file:
            print(f"  Keylog: {keylog_file}")
        print()

        self.server = TLSServer(
            port=port,
            kem_algorithm=kem_algorithm,
            sig_algorithm=sig_algorithm
        )

        self.server_thread = threading.Thread(
            target=self.server.start,
            kwargs={'debug': False, 'keylog_file': keylog_file},
            daemon=True
        )
        self.server_thread.start()

        print("等待 Server 啟動...")
        time.sleep(2)
        print("Server 已啟動\n")

    def stop_server(self):
        if self.server:
            print("\n停止 Server...")
            self.server.stop()
            self.server = None
            self.server_thread = None

    def start_capture(self, experiment_name):
        capture_config = self.patterns.get('capture', {})
        if not capture_config.get('enabled', False):
            return

        server_config = self.patterns.get('server', {})
        port = server_config.get('port', 4433)
        output_dir = capture_config.get('output_dir', 'data/pcaps')
        interface = capture_config.get('interface', None)

        print(f"\n啟動封包捕獲...")
        print(f"  Port: {port}")
        print(f"  輸出目錄: {output_dir}")
        if interface:
            print(f"  介面: {interface}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.pcap_filename = f"{experiment_name}_{timestamp}.pcap"

        self.capture = TrafficCapture(
            port=port,
            output_dir=output_dir,
            interface=interface
        )

        self.capture.output_file = f"{output_dir}/{self.pcap_filename}"

        self.capture.is_capturing = True
        kwargs = {
            'filter': f'tcp port {port}',
            'prn': self.capture._packet_callback,
            'store': True
        }
        if interface:
            kwargs['iface'] = interface

        from scapy.all import AsyncSniffer
        self.capture.sniffer = AsyncSniffer(**kwargs)
        self.capture.sniffer.start()

        time.sleep(1)
        print(f"  PCAP: {self.pcap_filename}\n")

    def stop_capture(self):
        if self.capture and self.capture.is_capturing:
            print("\n停止封包捕獲...")
            self.capture.stop()
            self.capture = None

    def generate_pattern(self, pattern_name, override=None):
        if pattern_name not in self.patterns['patterns']:
            raise ValueError(f"找不到模式: {pattern_name}")

        pattern = self.patterns['patterns'][pattern_name].copy()

        if override:
            pattern.update(override)

        server_config = self.patterns.get('server', {})
        server_config['host'] = 'localhost'

        AttackClass = self.load_attack_class(pattern_name)
        attack = AttackClass(pattern, server_config)

        return attack.execute()

    def run_experiment(self, experiment_file):
        experiment_path = Path(experiment_file)
        if not experiment_path.exists():
            raise FileNotFoundError(f"找不到實驗配置: {experiment_file}")

        with open(experiment_path, 'r', encoding='utf-8') as f:
            experiment = yaml.safe_load(f)

        experiment_name = experiment_path.stem

        print("=" * 70)
        print(f"實驗: {experiment.get('name', 'Unknown')}")
        print(f"描述: {experiment.get('description', 'No description')}")
        print("=" * 70)

        self.start_server()
        self.start_capture(experiment_name)

        try:
            sequences = experiment.get('sequences', [])
            for seq in sequences:
                pattern_name = seq['pattern']
                override = seq.get('override')

                print(f"\n執行模式: {pattern_name}")
                if override:
                    print(f"覆寫參數: {override}")

                result = self.generate_pattern(pattern_name, override)
                print(f"結果: {result}")

                wait_time = seq.get('wait', 0)
                if wait_time > 0:
                    print(f"等待 {wait_time} 秒...")
                    time.sleep(wait_time)

        finally:
            self.stop_capture()
            self.stop_server()

        print("\n" + "=" * 70)
        print("實驗完成!")
        print("=" * 70)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("\n使用方法:")
        print("  python traffic_generator.py <experiment_file>")
        print("\n範例:")
        print("  python traffic_generator.py configs/experiments/exp_01_benign.yaml")
        sys.exit(1)

    experiment_file = sys.argv[1]

    generator = TrafficGenerator()
    generator.run_experiment(experiment_file)
