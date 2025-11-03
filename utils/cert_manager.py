import os
import subprocess
from utils.settings import settings
from utils.openssl_cnf import get_minimal_openssl_cnf

class CertManager:
    def __init__(self, cert_dir=None):
        self.cert_dir = cert_dir or settings.cert['out_dir']
        os.makedirs(self.cert_dir, exist_ok=True)
        
    def generate_server_cert(self, algorithm=None, days=None):
        """生成 Server 憑證和私鑰"""

        algorithm = algorithm or settings.algorithms['default_signature']
        days = days or settings.openssl['days']

        algorithm = settings.get_algorithm(algorithm)
        
        key_file = os.path.join(self.cert_dir, 'server_key.pem')
        cert_file = os.path.join(self.cert_dir, 'server_cert.pem')
        
        openssl = settings.get_openssl_cmd()
        provider_path = settings.paths['oqs_provider_dir']
        
        print(f"生成 {algorithm} 私鑰...")
        result = subprocess.run([
            openssl, 'genpkey',
            '-algorithm', algorithm,
            '-out', key_file,
            '-provider-path', provider_path,
            '-provider', 'oqsprovider',
            '-provider', 'default',
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ 錯誤: {result.stderr}")
            raise RuntimeError("私鑰生成失敗")
        
        print(f"生成自簽憑證...")
        cfg_path = get_minimal_openssl_cnf()
        result = subprocess.run([
            openssl, 'req', '-new', '-x509',
            '-key', key_file,
            '-out', cert_file,
            '-days', str(days),
            '-subj', settings.openssl['subject'],
            '-config', cfg_path,
            '-provider-path', provider_path,
            '-provider', 'oqsprovider',
            '-provider', 'default',
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ 錯誤: {result.stderr}")
            raise RuntimeError("憑證生成失敗")
        
        print(f"✅ 憑證已生成:")
        print(f"   私鑰: {key_file}")
        print(f"   憑證: {cert_file}")
        
        return key_file, cert_file
    
    def verify_cert(self, cert_file):
        openssl = settings.get_openssl_cmd()
        provider_path = settings.paths['oqs_provider_dir']
        
        result = subprocess.run([
            openssl, 'x509',
            '-in', cert_file,
            '-text', '-noout',
            '-provider', 'oqsprovider',
            '-provider-path', provider_path
        ], capture_output=True, text=True)
        
        return result.stdout