from utils.cert_manager import CertManager

cert_mgr = CertManager()

print("開始生成 PQC 憑證...")
key, cert = cert_mgr.generate_server_cert()

print("\n憑證資訊:")
info = cert_mgr.verify_cert(cert)
print(info[:500])  # 只顯示前 500 字元  