from abc import ABC, abstractmethod
from core.normal_client import TLSClient


class BaseAttack(ABC):
    def __init__(self, config, server_config=None):
        self.config = config # 讀取yaml用
        self.server_config = server_config or {}

        host = self.server_config.get('host', 'localhost')
        port = self.server_config.get('port', 4433)
        kem_algorithm = self.server_config.get('kem_algorithm', 'mlkem768')
        sig_algorithm = self.server_config.get('sig_algorithm', 'mldsa65')

        self.client = TLSClient(
            host=host,
            port=port,
            kem_algorithm=kem_algorithm,
            sig_algorithm=sig_algorithm
        )

    @abstractmethod
    def execute(self):
        pass

    def get_pattern_info(self):
        return {
            'type': self.config.get('type', 'unknown'),
            'description': self.config.get('description', 'No description'),
            'connections': self.config.get('connections', 0)
        }
