from core.normal_server import TLSServer

print("啟動測試 Server...")
server = TLSServer(port=4433)
server.start()