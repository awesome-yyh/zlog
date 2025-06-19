# 多进程安全的日志记录

## 创建并激活虚拟环境
> uv venv -p 3.10
> source .venv/bin/activate

## 安装依赖
> uvi -r requirements.txt 

## 用法：
```py
from zlog import Zlog

zlog = Zlog("logs/testLog.log", level='debug').logging
zlog.debug("debug")
zlog.info("okkk")
zlog.warning("warning")
zlog.error("error")
zlog.critical("严重错误")
```