import random
import time
from attacks.base import BaseAttack


class SimpleTraffic(BaseAttack):
    def execute(self):
        connections = self.config.get('connections', 10) 
        size_config = self.config.get('size', {}) 
        size_min = size_config.get('min', 100)
        size_max = size_config.get('max', 1000)

        interval_config = self.config.get('interval', {}) 
        interval_min = interval_config.get('min', 0.1)
        interval_max = interval_config.get('max', 1.0)

        #  是否為突發模式（burst 模式會有 70% 機率短間隔，30% 機率正常間隔）
        burst = self.config.get('burst', False)

        pattern_info = self.get_pattern_info()
        print(f"\n開始執行: {pattern_info['description']}")
        print(f"總連線數: {connections}")
        print(f"封包大小範圍: {size_min} - {size_max} bytes")
        print(f"時間間隔範圍: {interval_min} - {interval_max} 秒")
        print(f"Burst 模式: {'是' if burst else '否'}\n")

        success_count = 0
        fail_count = 0

        for i in range(connections):
            size = random.randint(size_min, size_max)
            message = "X" * min(size, 10000) # 限制單次訊息最大 10KB

            try:
                self.client.connect(message=message, debug=False)
                success_count += 1
                print(f"[{i+1}/{connections}] [OK] 成功 - {size} bytes")
            except Exception as e:
                fail_count += 1
                print(f"[{i+1}/{connections}] [FAIL] 失敗: {e}")

            if i < connections - 1:
                if burst:
                    interval = random.uniform(interval_min, interval_max) if random.random() > 0.7 else 0
                else:
                    interval = random.uniform(interval_min, interval_max)

                time.sleep(interval)

        print(f"\n完成! 成功: {success_count}, 失敗: {fail_count}")
        return {'success': success_count, 'failed': fail_count}
