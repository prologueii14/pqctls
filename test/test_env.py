import subprocess
import os
from env.pqc_env import PQCEnvironment

# 確認環境已設定
print("PATH:", os.environ.get('PATH')[:200])
print("OPENSSL_MODULES:", os.environ.get('OPENSSL_MODULES'))

openssl = PQCEnvironment.get_openssl_cmd()
provider_path = PQCEnvironment.PATHS['oqs_provider']

print(f"\nOpenSSL: {openssl}")
print(f"Provider path: {provider_path}")

print("\n嘗試載入 oqsprovider...")
result = subprocess.run([
    openssl, 'list', '-providers',
    '-provider-path', provider_path,
    '-provider', 'oqsprovider'
], capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")