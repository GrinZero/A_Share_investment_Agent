from src.utils.logging_config import setup_logger
from .recorder import record

def fmtDate(date):
    return date.strftime('%Y%m%d')

def fmtDateTime(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')

logger = setup_logger('ChooseStock', record_list=record['log_record'])
