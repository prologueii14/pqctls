from utils.settings import settings

print("配置資訊:")
print(f"OpenSSL: {settings.get_openssl_cmd()}")
print(f"預設簽章算法: {settings.algorithms['default_signature']}")
print(f"Dilithium3 別名: {settings.get_algorithm('dilithium3')}")
print(f"憑證目錄: {settings.cert['out_dir']}")