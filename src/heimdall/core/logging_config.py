# --- START OF FILE heimdall/core/logging_config.py (复用自py_ai_core) ---

"""
日志系统配置模块。

该模块提供了一个核心函数 `setup_logging`，用于从一个 YAML 配置文件中
加载并应用日志配置。它还处理了配置文件不存在或加载失败时的回退逻辑，
确保应用在任何情况下都有一个基本的日志记录能力。
"""

# 1. 导入必要的标准库和第三方库
import logging
import logging.config
import os
import yaml


def setup_logging(
    config_path: str = "logging_config.yaml", default_level=logging.INFO
) -> None:
    """
    从指定的 YAML 文件中加载并初始化日志配置。
    """

    # 2. 确保日志文件所在的目录存在
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # 打印调试信息
    print(f"日志目录: {os.path.abspath(log_dir)}")
    print(f"配置文件路径: {os.path.abspath(config_path)}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"目录内容: {os.listdir('.')}")

    # 3. 检查指定的配置文件是否存在
    if os.path.exists(config_path):
        print(f"找到配置文件: {config_path}")
        with open(config_path, "rt", encoding="utf-8") as f:
            try:
                config = yaml.safe_load(f.read())
                print(f"配置文件内容: {config}")

                # 修复配置文件中的路径问题
                if "handlers" in config:
                    for handler_name, handler_config in config["handlers"].items():
                        if "filename" in handler_config:
                            # 确保日志文件路径是绝对路径
                            handler_config["filename"] = os.path.abspath(
                                handler_config["filename"]
                            )
                            print(
                                f"修复处理器 {handler_name} 的文件路径: {handler_config['filename']}"
                            )

                logging.config.dictConfig(config)
                logger = logging.getLogger(__name__)
                logger.info("日志系统已成功从 '%s' 文件加载配置。", config_path)
                print("日志配置加载成功")
            except Exception as e:
                print(f"加载日志配置失败: {e}")
                import traceback

                traceback.print_exc()
                # 回退到基础配置
                logging.basicConfig(
                    level=default_level,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                )
                logger = logging.getLogger(__name__)
                logger.error(
                    "从 '%s' 加载日志配置失败: %s。已回退到基础配置。",
                    config_path,
                    e,
                    exc_info=True,
                )
    else:
        print(f"配置文件不存在: {config_path}")
        # 回退到基础配置
        logging.basicConfig(
            level=default_level, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logger = logging.getLogger(__name__)
        logger.warning("日志配置文件 '%s' 未找到。已回退到基础配置。", config_path)

    # 4. 测试日志系统
    test_logger = logging.getLogger("heimdall.test")
    test_logger.info("日志系统测试消息")
    print("日志系统测试完成")

    # 5. 检查日志文件是否创建
    if os.path.exists("logs/app.log"):
        print("OK: app.log 文件已创建")
        with open("logs/app.log", "r", encoding="utf-8") as f:
            content = f.read()
            print(f"app.log 内容长度: {len(content)} 字符")
    else:
        print("ERROR: app.log 文件未创建")


# --- END OF FILE heimdall/core/logging_config.py ---