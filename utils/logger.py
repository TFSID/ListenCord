import logging
import sys
from pathlib import Path
from typing import Optional

class Logger:
    """Utility class untuk logging management"""
    
    _instances = {}
    
    @classmethod
    def get_logger(cls, name: str, log_file: Optional[str] = None, level: str = 'INFO') -> logging.Logger:
        """Get atau create logger instance"""
        if name not in cls._instances:
            cls._instances[name] = cls._create_logger(name, log_file, level)
        return cls._instances[name]
    
    @staticmethod
    def _create_logger(name: str, log_file: Optional[str] = None, level: str = 'INFO') -> logging.Logger:
        """Create new logger instance"""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler jika ditentukan
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
