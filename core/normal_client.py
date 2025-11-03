import subprocess
from utils.settings import settings
import os

class TLSClient:
    def __init__(self, host='localhost', port=4433, kem_algorithm=None):
        self.host = host
        self.port = port
        self.kem_algorithm = kem_algorithm or settings.algorithms['default_kem']
    
    def connect(self, message=None, debug=False, keylog_file=None):
        """
        連接到 TLS Server
        
        Args:
            message: 要發送的訊息
            debug: 是否顯示 debug 資訊（-state -msg）
            keylog_file: 儲存 session keys 的檔案路徑
        """
        openssl = settings.get_openssl_cmd()
        provider_path = settings.paths['oqs_provider_dir']
        
        kem = settings.get_algorithm(self.kem_algorithm)
        
        print("=" * 60)
        print(f"🔌 連接 PQC-TLS Server")
        print("=" * 60)
        print(f"目標:          {self.host}:{self.port}")
        print(f"KEM 算法:      {kem}")
        if debug:
            print(f"Debug 模式:    ✅ 啟用")
        if keylog_file:
            print(f"Keylog 檔案:   {keylog_file}")
        print("=" * 60)
        
        cmd = [
            openssl, 's_client',
            '-connect', f'{self.host}:{self.port}',
            '-tls1_3',
            '-groups', kem,
            '-provider-path', provider_path,
            '-provider', 'default',
            '-provider', 'oqsprovider',
            '-CAfile', 'certs/server_cert.pem',
        ]
        
        # Debug 模式
        if debug:
            cmd.extend(['-state', '-msg'])
        
        # Keylog
        if keylog_file:
            keylog_abs = os.path.abspath(keylog_file)
            os.makedirs(os.path.dirname(keylog_abs), exist_ok=True)
            cmd.extend(['-keylogfile', keylog_abs])
        
        print("\n正在連接...\n")
        
        try:
            if message:
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate(input=message + "\n", timeout=120)
                
                print("連線成功！")
                print("\n=== 握手資訊 ===")
                for line in stderr.split('\n'):
                    if any(keyword in line for keyword in ['Protocol', 'Cipher', 'Server Temp Key', 'Peer signing', 'Peer public key']):
                        print(line)
                
                if stdout:
                    print("\n=== Server 回應 ===")
                    print(stdout[:500])
                
            else:
                process = subprocess.Popen(cmd)
                process.wait()
                
        except subprocess.TimeoutExpired:
            print("⏱️  連線超時")
        except KeyboardInterrupt:
            print("\n\n⚠️  連線中斷")
        except Exception as e:
            print(f"❌ 連線錯誤: {e}")

if __name__ == "__main__":
    client = TLSClient()
    client.connect(message="GET / HTTP/1.0", debug=True, keylog_file='data/keys/client_keys.log')