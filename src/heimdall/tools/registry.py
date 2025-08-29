# py_ai_core\tools\registry.py
import inspect
import json
import logging  # 👈 1. 导入 logging 模块
from typing import Callable, Dict, Any, List

# 2. 在模块顶部，获取一个 logger 实例
#    __name__ 在这里的值会是 'py_ai_core.tools.registry' (假设文件路径是这样)
logger = logging.getLogger(__name__)

TYPE_MAPPING = {"str": "string", "int": "integer", "float": "number", "bool": "boolean"}


class ToolRegistry:
    def __init__(self):
        """工具注册中心的构造函数"""
        self.tools: Dict[str, Callable] = {}
        self.tool_schemas: List[Dict[str, Any]] = []
        # 在构造函数中记录初始化信息
        logger.info("工具注册中心 (ToolRegistry) 已初始化。")

    def register(self, func: Callable):
        """
        注册一个新工具，并根据其签名和文档字符串生成 schema。
        """
        tool_name = func.__name__

        # 3. 使用 logger.info 替换 print，并使用格式化字符串
        logger.info("开始注册新工具：%s", tool_name)

        self.tools[tool_name] = func

        # --- 生成 Schema 的逻辑 (这部分逻辑保持不变) ---
        sig = inspect.signature(func)
        doc = inspect.getdoc(func)
        description = doc.split("\n")[0] if doc else ""

        # 记录调试信息，这在排查 schema 生成问题时非常有用
        logger.debug("工具 '%s' 的描述: '%s'", tool_name, description)

        parameters = {"type": "object", "properties": {}, "required": []}
        for name, param in sig.parameters.items():
            param_type = TYPE_MAPPING.get(param.annotation.__name__, "string")
            parameters["properties"][name] = {
                "type": param_type,
                "description": f"参数: {name}",  # 中文描述
            }
            if param.default is inspect.Parameter.empty:
                parameters["required"].append(name)

        logger.debug("为工具 '%s' 生成的参数 schema: %s", tool_name, parameters)

        tool_schema = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": description,
                "parameters": parameters,
            },
        }
        self.tool_schemas.append(tool_schema)

        # 使用 logger.info 记录成功信息
        logger.info("工具 '%s' 已成功注册并生成 schema。", tool_name)

        return func

    def get_tool(self, name: str) -> Callable | None:
        """根据名称获取已注册的工具函数"""
        tool = self.tools.get(name)
        if tool:
            logger.debug("成功获取工具: %s", name)
        else:
            # 对于未找到的情况，使用 warning 级别更合适
            logger.warning("尝试获取一个未注册的工具: %s", name)
        return tool

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """获取所有已注册工具的 schema 列表"""
        logger.debug(
            "正在获取所有已注册工具的 schema，共 %d 个。", len(self.tool_schemas)
        )
        return self.tool_schemas


# 实例化对象
tool_registry = ToolRegistry()


# 装饰器函数
def tool(func: Callable):
    """
    一个用于注册工具的装饰器。
    用法:
    @tool
    def my_function(...):
        ...
    """
    # 装饰器本身不需要日志，因为它只是调用了 register 方法
    return tool_registry.register(func)
