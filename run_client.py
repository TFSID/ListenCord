import sys
from client.socket_client import SocketClient
from config import Config

def main():
    """Run socket client"""
    if len(sys.argv) > 1:
        host = sys.argv[1]
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8888
    else:
        # Use default config
        _, socket_config = Config.from_env()
        host = socket_config.host
        port = socket_config.port
    
    client = SocketClient(host, port)
    if client.connect():
        client.listen()

if __name__ == "__main__":
    main()
