import os
import subprocess
from utils.settings import settings
from utils.cert_manager import CertManager

class TLSServer:
    def __init__(self, port=4433, kem_algorithm=None, sig_algorithm=None):
        self.port = port
        self.kem_algorithm = kem_algorithm or settings.algorithms['default_kem']
        self.sig_algorithm = sig_algorithm or settings.algorithms['default_signature']
        self.process = None
        
        self.cert_manager = CertManager()
        self.key_file = os.path.join(settings.cert['out_dir'], 'server_key.pem')
        self.cert_file = os.path.join(settings.cert['out_dir'], 'server_cert.pem')
        
        self._ensure_certificates()
    
    def _ensure_certificates(self):
        if not os.path.exists(self.key_file) or not os.path.exists(self.cert_file):
            print("⚠️  憑證不存在，開始生成...")
            self.cert_manager.generate_server_cert(algorithm=self.sig_algorithm)
        else:
            print("✅ 使用現有憑證")
    
    def start(self, debug=False, keylog_file=None):
        """
        啟動 TLS Server
        
        Args:
            debug: 是否顯示 debug 資訊（-state -msg）
            keylog_file: 儲存 session keys 的檔案路徑（用於 Wireshark 解密）
        """
        openssl = settings.get_openssl_cmd()
        provider_path = settings.paths['oqs_provider_dir']
        
        kem = settings.get_algorithm(self.kem_algorithm)
        
        print("=" * 60)
        print(f"🚀 啟動 PQC-TLS Server")
        print("=" * 60)
        print(f"Port:          {self.port}")
        print(f"KEM 算法:      {kem}")
        print(f"簽章算法:      {self.sig_algorithm}")
        print(f"憑證:          {self.cert_file}")
        print(f"私鑰:          {self.key_file}")
        if debug:
            print(f"Debug 模式:    ✅ 啟用")
        if keylog_file:
            print(f"Keylog 檔案:   {keylog_file}")
        print("=" * 60)
        
        cert_file_abs = os.path.abspath(self.cert_file)
        key_file_abs = os.path.abspath(self.key_file)
        
        cmd = [
            openssl, 's_server',
            '-accept', str(self.port),
            '-cert', cert_file_abs,
            '-key', key_file_abs,
            '-tls1_3',
            '-groups', kem,
            '-provider-path', provider_path,
            '-provider', 'default',
            '-provider', 'oqsprovider',
            '-WWW',
        ]
        
        # Debug 模式
        if debug:
            cmd.extend(['-state', '-msg'])
        
        # Keylog（用於 Wireshark 解密）
        if keylog_file:
            keylog_abs = os.path.abspath(keylog_file)
            os.makedirs(os.path.dirname(keylog_abs), exist_ok=True)
            cmd.extend(['-keylogfile', keylog_abs])
        
        try:
            print("\n等待連線... (Ctrl+C 停止)\n")
            self.process = subprocess.Popen(cmd)
            self.process.wait()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  收到中斷信號，正在關閉 Server...")
            self.stop()
        except Exception as e:
            print(f"\n❌ Server 錯誤: {e}")
            self.stop()
    
    def stop(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            print("✅ Server 已停止")

if __name__ == "__main__":
    server = TLSServer(port=4433)
    server.start(debug=True, keylog_file='data/keys/server_keys.log')