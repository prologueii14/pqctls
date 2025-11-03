import os
import yaml
from pathlib import Path

class Settings:
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        config_path = Path(__file__).parent.parent / 'serversetting.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            raw = yaml.safe_load(f)
        self._config = self._expand_variables(raw)
        # 自動設定環境變數
        self._setup_environment()
    
    def _expand_variables(self, obj, context=None):
        if context is None:
            context = obj
        if isinstance(obj, dict):
            return {k: self._expand_variables(v, context) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._expand_variables(item, context) for item in obj]
        elif isinstance(obj, str) and '${' in obj:
            result = obj
            import re
            for match in re.finditer(r'\$\{([^}]+)\}', obj):
                var_path = match.group(1).split('.')
                value = context
                for key in var_path:
                    value = value[key]
                result = result.replace(match.group(0), str(value))
            return result
        return obj
    
    def _setup_environment(self):
        paths = self._config['paths']
        os.environ['PATH'] = f"{paths['liboqs_bin']};{paths['openssl_bin']};{os.environ.get('PATH', '')}"
        os.environ['OPENSSL_MODULES'] = paths['oqs_provider_dir']
    
    @property
    def paths(self):
        return self._config['paths']
    
    @property
    def openssl(self):
        return self._config['openssl']
    
    @property
    def algorithms(self):
        return self._config['algorithms']
    
    @property
    def cert(self):
        return self._config['cert']
    
    def get_algorithm(self, name):
        alias_map = self.algorithms.get('alias_map', {})
        return alias_map.get(name, name)
    
    def get_openssl_cmd(self):
        return self.paths['openssl_exe']

# 單例
settings = Settings()