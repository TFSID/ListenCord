import socket
from utils.logger import Logger

class SocketClient:
    """Client untuk connect ke socket server"""
    
    def __init__(self, host: str = 'localhost', port: int = 8888):
        self.host = host
        self.port = port
        self.socket = None
        self.logger = Logger.get_logger(self.__class__.__name__)
    
    def connect(self) -> bool:
        """Connect ke socket server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.logger.info(f"Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Error connecting: {e}")
            return False
    
    def listen(self) -> None:
        """Listen untuk data dari server"""
        if not self.socket:
            self.logger.error("Not connected to server")
            return
        
        try:
            while True:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                message = data.decode('utf-8')
                if message.strip() == "HEARTBEAT":
                    continue
                
                print(f"\n{'='*50}")
                print("NEW MESSAGE RECEIVED:")
                print(f"{'='*50}")
                print(message)
                
        except KeyboardInterrupt:
            self.logger.info("Client stopped by user")
        except Exception as e:
            self.logger.error(f"Error: {e}")
        finally:
            self.disconnect()
    
    def disconnect(self) -> None:
        """Disconnect dari server"""
        if self.socket:
            self.socket.close()
            self.logger.info("Disconnected from server")
