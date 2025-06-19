'''
Author: yangyahe owyangyahe@126.com
Date: 2024-08-04 16:13:57
LastEditors: yangyahe yangyahe@midu.com
LastEditTime: 2025-06-19 16:13:22
Description: 日志模块，提供多进程安全的日志记录功能。
'''
import os
import logging
import datetime
import socket
from concurrent_log_handler import ConcurrentTimedRotatingFileHandler
from colorama import Fore, Style, init  


# 初始化 colorama  
# autoreset=True 使得每次打印后自动重置颜色，避免后续输出受到影响。
init(autoreset=True)  


class ColoredFormatter(logging.Formatter):  
    # 定义不同日志级别对应的颜色  
    COLORS = {  
        "DEBUG": Fore.MAGENTA,  
        "INFO": Fore.GREEN,  
        "WARNING": Fore.YELLOW,  
        "ERROR": Fore.RED,  
        "CRITICAL": Fore.RED + Style.BRIGHT,  
    }  

    def format(self, record): 
        """格式化日志记录""" 
        # 获取对应级别的颜色  
        color = self.COLORS.get(record.levelname, "")  
        # 为消息添加颜色  
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"  
        # 调用父类的 format 方法  
        return super().format(record)  


class Zlog:
    """多进程安全的日志类
    
    typical usage example:
    
    :zlog = Zlog("logs/testLog.log").logging
    :zlog.info("okkk")
    :zlog.warning("warning")
    :zlog.error("error")

    Args:

    :file_name(str): 设置日志输出到文件的文件名
    :level(str): 设置日志级别，只输出大于等于该等级的日志
    :backupCount(int): 保留最近的多少份的日志文件，更早期的删除，0表示全保留
    """
    def __init__(self, file_name: str, level="info", backupCount: int = 0, add_color: bool = True):
        # 有可能路径中的文件夹不存在，故需创建（文件会自动创建，文件夹不会）
        file_name = os.path.abspath(file_name)
        dir_path = os.path.dirname(file_name)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)

        level_relations = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'crit': logging.CRITICAL
        }  # 日志级别关系映射

        self.logging = logging.getLogger(file_name)  # 创建Logger实例(log记录器)
        # 为避免创建了多个同file_name的zlog对象时，日志会重复打印，故需先判断
        if not self.logging.handlers:
            self.logging.setLevel(level_relations.get(level))  # 设置日志级别
            hostname = socket.gethostname()
            format_str = f'{hostname} - %(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
            if add_color:
                formatter = ColoredFormatter(format_str)  # 使用自定义的 ColoredFormatter, 格式化器，设置日志内容的组成结构和消息字段。
            else:
                formatter = logging.Formatter(format_str)  # 默认的格式化器
            
            formatter.converter = self.local_time
            self.logging.makeRecord = self.log_with_relative_path

            # # Handlers用于将日志发送至目的地
            # 往屏幕上输出日志
            sh = logging.StreamHandler()
            sh.setFormatter(formatter)
            self.logging.addHandler(sh)

            # 往文件里写入日志
            # 'D' 从应用程序启动时间开始, 每 24 小时滚动一次日志
            # 'midnight' 每天午夜滚动日志
            rotateHandler = ConcurrentTimedRotatingFileHandler(
                filename=file_name, 
                when='midnight', 
                interval=1,
                backupCount=backupCount, 
                encoding="utf-8")
            rotateHandler.setFormatter(formatter)
            self.logging.addHandler(rotateHandler)
    
    def local_time(self, *args):
        utc_plus_8 = datetime.timezone(datetime.timedelta(hours=8))  # 中国时区为UTC+8
        local_dt = datetime.datetime.now(utc_plus_8)
        return local_dt.timetuple()
    
    def log_with_relative_path(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None):
        """定义一个辅助函数，用于将绝对路径转换为相对路径
        """
        # 创建原始的LogRecord对象
        record = logging.LogRecord(name, level, fn, lno, msg, args, exc_info, func, sinfo)
        # 更新LogRecord对象的pathname属性为相对路径
        record.pathname = os.path.relpath(record.pathname)
        return record


if __name__ == "__main__":
    # 用法：
    zlog = Zlog("logs/testLog.log", level='debug').logging
    zlog.debug("debug")
    zlog.info("okkk")
    zlog.warning("warning")
    zlog.error("error")
    zlog.critical("严重错误")
