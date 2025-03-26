
from datetime import datetime,timedelta
import time
from concurrent.futures import ThreadPoolExecutor, wait
from src.trade.core.context import Context
import pandas_market_calendars as mcal
from src.core.recorder import reset_record, send_record, process_record_queue
from .utils import logger

# 存储注册的任务，使用列表存储元组，保持注册顺序
tasks = []  # [(task, time_str, type, day), ...]
# 创建线程池
executor = ThreadPoolExecutor(max_workers=5)

def run_daily(fn: callable, time: str):
    """每天运行"""
    tasks.append((fn, time, "daily", None))

def run_weekly(fn: callable, day: int, time: str):
    """每周运行"""
    tasks.append((fn, time, "weekly", day))

def should_run_task(current_time: datetime, task_time: str) -> bool:
    """检查是否应该执行任务"""
    
    task_hour, task_minute = map(int, task_time.split(':'))
    res = (current_time.hour == task_hour and 
            current_time.minute == task_minute)
    # logger.info(f"检查任务是否应该执行: 当前时间 {current_time}, 任务时间 {task_time}, 结果 {res}")
    return res

def execute_task(task, context, task_type="daily"):
    """在线程池中执行任务"""
    try:
        task(context)
    except Exception as e:
        import traceback
        error_msg = f"\n执行 {task.__name__} 任务出错:\n"
        error_msg += f"错误类型: {type(e).__name__}\n"
        error_msg += f"错误信息: {str(e)}\n"
        error_msg += "详细堆栈:\n"
        error_msg += traceback.format_exc()
        logger.info(error_msg)

def is_trading_day(date):
    # 获取上交所（SSE）日历
    sse = mcal.get_calendar('SSE')
    # 生成指定日期范围的交易日历
    schedule = sse.schedule(start_date=date, end_date=date)
    return not schedule.empty

def run_scheduler(test_mode=False, start_time=None, end_time=None):
    try:
        while True:
            try:
                if test_mode:
                    if start_time >= end_time:
                        logger.info("测试完成")
                        break
                    context = Context(current_dt=start_time)
                    current_time = start_time
                    # 模拟时间前进一分钟
                    start_time += timedelta(minutes=1)
                else:
                    context = Context()
                    current_time = context.current_dt
                
                # 根据当前时间判断是否是交易日，如果不是，sleep 到下一日 00:00
                if not is_trading_day(current_time):
                    logger.info(f"{current_time} 不是交易日，等待到下一日 00:00")
                    if test_mode:
                        # 测试模式下，跳到下一天，并跳到 09:00
                        start_time += timedelta(days=1)
                        continue
                    else:
                        # 计算到下一天凌晨的秒数
                        tomorrow = current_time + timedelta(days=1)
                        tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
                        sleep_seconds = (tomorrow - current_time).total_seconds()
                        time.sleep(sleep_seconds)
                        current_time = datetime.now()
                        continue
                
                # 非交易时段打印状态
                current_hour = current_time.hour
                if (current_hour >= 16 or current_hour < 8) and current_time.minute % 5 == 0:
                    logger.info(f"当前处于非交易时段 - {current_time}")
                    if test_mode:
                        # 测试模式下，如果 <= 8，则跳到 9；否则跳到第二天
                        if current_hour <= 8:
                            start_time = start_time.replace(hour=9, minute=0, second=0, microsecond=0)
                        else:
                            start_time += timedelta(days=1)
                            start_time = start_time.replace(hour=9, minute=0, second=0, microsecond=0)
                        continue
                
                current_weekday = current_time.weekday() + 1
                
                # 收集当前时间需要执行的所有任务
                futures = []
                for task, time_str, task_type, day in tasks:
                    if should_run_task(current_time, time_str):
                        if task_type == "daily" or (task_type == "weekly" and day == current_weekday):
                            logger.info(f"准备执行任务: {task.__name__}, 时间: {time_str}, 类型: {task_type}")
                            future = executor.submit(execute_task, task, context, task_type)
                            futures.append(future)
                
                # 等待所有任务完成后再进入下一分钟
                if futures:
                    wait(futures)
                
                # 处理队列中的记录并发送
                process_record_queue()  # 确保处理所有队列中的记录
                send_record()
                
                if not test_mode:
                    # 等待到下一分钟
                    time.sleep(60 - current_time.second)
                
                reset_record()
                    
            except Exception as e:
                logger.info(f"调度器运行出错: {str(e)}")
                if test_mode:
                    raise  # 测试模式下直接抛出异常
                time.sleep(60)  # 生产环境下等待一分钟后继续
                
    except KeyboardInterrupt:
        logger.info("调度器被手动停止")
    except Exception as e:
        logger.info(f"调度器致命错误: {str(e)}")
    finally:
        # 确保发送最后的记录
        process_record_queue()
        send_record()
        executor.shutdown(wait=True)  # 确保所有任务都完成后关闭线程池

if __name__ == "__main__":
    from src.trade.close_account import close_account
    from src.trade.prepare_stock_list import prepare_stock_list
    from src.trade.trade_afternoon import trade_afternoon
    from src.trade.sell_stocks import sell_stocks
    from src.trade.weekly_adjustment import weekly_adjustment
    from src.trade.print_position_info import print_position_info
    from src.trade.config import g
    
    # g['in_history'] = True
    run_daily(prepare_stock_list, '9:05')
    run_daily(trade_afternoon, time='14:00') #检查持仓中的涨停股是否需要卖出
    run_daily(sell_stocks, time='10:00') # 止损函数
    run_daily(close_account, '14:50')
    run_weekly(weekly_adjustment,3,'10:00')
    run_daily(print_position_info, '15:15')
    run_scheduler(test_mode=True, start_time=datetime(2025, 3, 26), end_time=datetime(2025, 3, 27))