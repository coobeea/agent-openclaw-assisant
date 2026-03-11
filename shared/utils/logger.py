"""
日志工具
提供统一的日志记录功能
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from colorlog import ColoredFormatter


def setup_logger(
    name: str,
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    color: bool = True
) -> logging.Logger:
    """
    设置并返回一个配置好的 logger
    
    Args:
        name: logger 名称
        log_level: 日志级别 (DEBUG, INFO, WARN, ERROR)
        log_file: 日志文件路径（可选）
        color: 是否使用彩色输出
    
    Returns:
        配置好的 logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    if color:
        # 彩色格式
        formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s [%(levelname)s]%(reset)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
    else:
        # 普通格式
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件 handler（如果指定）
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_instance_logger(
    instance_id: str,
    log_level: str = "INFO",
    workspace_root: Optional[Path] = None,
    log_file_name: str = "openclaw.log"
) -> logging.Logger:
    """
    获取实例专用的 logger
    
    注意：日志文件路径应该从配置中读取或由调用方指定，
    而不是硬编码。如果实例使用 OpenClaw 自己的日志系统，
    这个函数可能不需要指定 log_file。
    
    Args:
        instance_id: 实例 ID
        log_level: 日志级别
        workspace_root: 工作空间根目录（从配置中读取）
        log_file_name: 日志文件名（默认 openclaw.log）
    
    Returns:
        配置好的 logger
    """
    # 如果指定了工作空间，尝试写入日志文件
    log_file = None
    if workspace_root:
        workspace_root = Path(workspace_root)
        instance_path = workspace_root / instance_id
        
        # 尝试在实例目录下的 logs/ 目录写入日志
        # 如果 OpenClaw 没有创建 logs/ 目录，日志只输出到控制台
        if instance_path.exists():
            log_dir = instance_path / "logs"
            if log_dir.exists() or log_dir.parent.exists():
                log_dir.mkdir(exist_ok=True)
                log_file = log_dir / log_file_name
    
    return setup_logger(
        name=f"openclaw.{instance_id}",
        log_level=log_level,
        log_file=log_file,
        color=True
    )


# 默认 logger（用于技能包脚本）
default_logger = setup_logger("openclaw", color=True)


if __name__ == "__main__":
    # 测试代码
    logger = setup_logger("test", log_level="DEBUG")
    
    logger.debug("这是一条调试信息")
    logger.info("这是一条普通信息")
    logger.warning("这是一条警告信息")
    logger.error("这是一条错误信息")
    logger.critical("这是一条严重错误信息")
    
    # 测试实例 logger
    instance_logger = get_instance_logger("openclaw-test-01")
    instance_logger.info("实例日志测试")
