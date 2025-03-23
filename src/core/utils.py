from src.utils.logging_config import setup_logger

def fmtDate(date):
    return date.strftime('%Y%m%d')

def fmtDateTime(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')

logger = setup_logger('-')
