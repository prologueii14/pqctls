from core.normal_client import TLSClient

print("測試 PQC-TLS 連線...\n")

client = TLSClient(host='localhost', port=4433)
client.connect(message="GET / HTTP/1.0")