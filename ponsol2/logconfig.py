# -*- coding:utf-8 -*-
'''
__author__ = 'XD'
__mtime__ = 2021/1/18
__project__ = Pon-Sol2
Fix the Problem, Not the Blame.
'''
# -*- coding:utf-8 -*-
# 文件写法参考：https://github.com/dls-controls/python-logging-configuration/blob/master/logconfig.py
# 具体配置自写
import json
import yaml
import logging
import logging.config
import os

default_config = {
    "version": 1,  # 目前只有 1 有效，用于以后兼容性
    "incremental": False,  # 是否在运行中时修改配置, 默认 False
    "disable_existing_loggers": True,  # 是否禁用任何非根的所有 Logger, 默认 False
    "formatters": {  # 格式化生成器(格式器)
        "default": {
            "format": "%(name)s %(asctime)s [%(filename)s %(funcName)s()] <%(levelname)s>: %(message)s",
        },
        "brief": {
            "format": "%(name)s [%(funcName)s()] <%(levelname)s>: %(message)s",
        }
    },
    "filters": {},  # 过滤器，需要自定义类，一般不会用到
    "handlers": {
        "console": {  # 控制台
            "class": "logging.StreamHandler",
            "formatter": "brief",
            "level": "DEBUG",
            "stream": "ext://sys.stdout",
        },
        "file_debug": {  # 输出到文件
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "level": "DEBUG",
            "filename": "debug_logger.log",  # 必选, 文件名称
            "encoding": "utf8",
            "maxBytes": 10485760,  # 日志文件最大个数 1024B * 1024 * 10 = 10MB
            "backupCount": 10,  # 日志文件最大个数
        },
        "file_info": {  # 输出到文件
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "level": "INFO",
            "filename": "info_logger.log",  # 必选, 文件名称
            "encoding": "utf8",
            "maxBytes": 10485760,  # 日志文件最大个数 1024B * 1024 * 10 = 10MB
            "backupCount": 10,  # 日志文件最大个数
        },
    },
    "loggers": {
        "ponsol": {
            "level": "DEBUG",
            "handlers": ["console", "file_debug", "file_info"],
            "propagate": False,  # 是否传给父级
        }
    },
}


def setup_logging(
        default_log_config=None,
        is_yaml=True,
        default_level=logging.INFO,
        env_key='LOG_CFG',
):
    """Setup logging configuration
    Call this only once from the application main() function or __main__ module!
    This will configure the python logging module based on a logging configuration
    in the following order of priority:
       1. Log configuration file found in the environment variable specified in the `env_key` argument.
       2. Log configuration file found in the `default_log_config` argument.
       3. Default log configuration found in the `logconfig.default_config` dict.
       4. If all of the above fails: basicConfig is called with the `default_level` argument.
    Args:
        default_log_config (Optional[str]): Path to log configuration file.
        env_key (Optional[str]): Environment variable that can optionally contain
            a path to a configuration file.
        default_level (int): logging level to set as default. Ignored if a log
            configuration is found elsewhere.
        is_yaml (bool): weather config file is a yaml file
    Returns: None
    """
    dict_config = None
    logconfig_filename = default_log_config
    env_var_value = os.getenv(env_key, None)

    if env_var_value is not None:
        logconfig_filename = env_var_value

    if default_config is not None:
        dict_config = default_config

    if logconfig_filename is not None and os.path.exists(logconfig_filename):
        with open(logconfig_filename, 'rt', encoding="utf8") as f:
            if is_yaml:
                file_config = yaml.load(f, Loader=yaml.FullLoader)
            else:
                file_config = json.load(f)
        if file_config is not None:
            dict_config = file_config

    if dict_config is not None:
        logging.config.dictConfig(dict_config)
    else:
        logging.basicConfig(level=default_level)


if __name__ == '__main__':
    with open("./logconfig.yaml", "w") as f:
        yaml.dump(default_config, f)