import logging
import sys
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path

class DailyRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='midnight', interval=1, backupCount=0, 
                 encoding=None, delay=False, utc=False, atTime=None):
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

def setup_bot_logging():
    logger = logging.getLogger("neuro_hr")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False
    

    formatter = logging.Formatter('%(levelname)s - %(message)s')
    
    file_handler = DailyRotatingFileHandler(
        'bot.log', 
        when='midnight', 
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG) 
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger