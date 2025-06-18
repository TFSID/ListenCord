import socket
import threading
import asyncio
from typing import List, Set
from config import SocketConfig
from models.message import DiscordMessage
from utils.logger import Logger

class SocketServer:
    """Socket server untuk broadcast message ke clients"""
    
    def __init__(self, config: SocketConfig):
        self.config = config
        self.logger = Logger.get_logger(self.__class__.__name__)
        
        self.server_socket: socket.socket = None
        self.clients: List[socket.socket] = []
        self.server_running = False
        self._server_thread = None
    
    async def start(self) -> None:
        """Start socket server"""
        if self.server_running:
            self.logger.warning("Socket server already running")
            return
        
        self._server_thread = threading.Thread(target=self._run_server, daemon=True)
        self._server_thread.start()
        
        # Wait a bit untuk server start
        await asyncio.sleep(0.1)
        self.logger.info(f"Socket server started on {self.config.host}:{self.config.port}")
    
    def stop(self) -> None:
        """Stop socket server"""
        self.server_running = False
        
        # Close semua client connections
        for client in self.clients.copy():
            self._disconnect_client(client)
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception as e:
                self.logger.error(f"Error closing server socket: {e}")
        
        self.logger.info("Socket server stopped")
    
    def _run_server(self) -> None:
        """Run server loop dalam thread terpisah"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.config.host, self.config.port))
            self.server_socket.listen(self.config.max_connections)
            
            self.server_running = True
            
            while self.server_running:
                try:
                    self.server_socket.settimeout(1.0)  # Timeout untuk graceful shutdown
                    client_socket, address = self.server_socket.accept()
                    
                    self.logger.info(f"Client connected from {address}")
                    self.clients.append(client_socket)
                    
                    # Start thread untuk handle client
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    continue  # Continue loop untuk check server_running
                except Exception as e:
                    if self.server_running:
                        self.logger.error(f"Error accepting client: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error starting socket server: {e}")
        finally:
            self.server_running = False
    
    def _handle_client(self, client_socket: socket.socket, address: tuple) -> None:
        """Handle individual client connection"""
        try:
            while self.server_running:
                # Send heartbeat
                try:
                    client_socket.send(b"HEARTBEAT\n")
                    threading.Event().wait(self.config.heartbeat_interval)
                except Exception:
                    break
                    
        except Exception as e:
            self.logger.debug(f"Client {address} disconnected: {e}")
        finally:
            self._disconnect_client(client_socket)
    
    def _disconnect_client(self, client_socket: socket.socket) -> None:
        """Disconnect client dan cleanup"""
        if client_socket in self.clients:
            self.clients.remove(client_socket)
        
        try:
            client_socket.close()
        except Exception:
            pass
    
    async def broadcast_message(self, message_data: DiscordMessage) -> None:
        """Broadcast message ke semua connected clients"""
        if not self.clients:
            return
        
        message_json = message_data.to_json()
        message_bytes = f"{message_json}\n".encode('utf-8')
        
        disconnected_clients = []
        
        for client in self.clients.copy():
            try:
                client.send(message_bytes)
            except Exception as e:
                self.logger.warning(f"Failed to send to client: {e}")
                disconnected_clients.append(client)
        
        # Cleanup disconnected clients
        for client in disconnected_clients:
            self._disconnect_client(client)
    
    @property
    def client_count(self) -> int:
        """Get jumlah connected clients"""
        return len(self.clients)
    
    @property
    def is_running(self) -> bool:
        """Check apakah server sedang running"""
        return self.server_running
