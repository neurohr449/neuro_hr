import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path

class DailyRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='midnight', interval=1, backupCount=0, 
                 encoding=None, delay=False, utc=False, atTime=None):
        # Создаем папку для логов
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        super().__init__(
            str(log_dir / filename), 
            when=when, 
            interval=interval, 
            backupCount=backupCount,
            encoding=encoding, 
            delay=delay, 
            utc=utc, 
            atTime=atTime
        )

def setup_advanced_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Обработчик с ежедневной ротацией
    file_handler = DailyRotatingFileHandler(
        'bot.log', 
        when='midnight', 
        interval=1,
        backupCount=7,  # Хранить логи за 7 дней
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.suffix = "%Y-%m-%d"
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger