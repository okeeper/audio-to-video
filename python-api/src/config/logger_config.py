import logging
from logging.handlers import TimedRotatingFileHandler
import os

import utils.path_utils as path_utils


def setup_logger(name=None):
    """
    配置日志记录器
    :param name: 记录器名称，默认为root记录器
    :return: 配置好的记录器
    """
    # 获取项目根目录
    project_root = path_utils.get_project_root()
    # 创建logs目录（相对于项目根目录）
    log_dir = project_root / 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # 如果没有指定名称，使用root记录器
    logger = logging.getLogger(name)
    
    # 如果记录器已经有处理器，说明已经配置过，直接返回
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 配置按天滚动的文件处理器
    file_handler = TimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),  # 使用项目根目录相对路径
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.suffix = "%Y%m%d"  # 日志文件后缀格式
    
    # 配置控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 清除可能存在的旧处理器
    logger.handlers.clear()
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 