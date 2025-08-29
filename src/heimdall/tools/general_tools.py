# py_ai_core/tools/general_tools.py

# 1. 导入 logging 和 tool 装饰器
import logging
from .registry import tool
from datetime import datetime

# 2. 获取模块级 logger 实例
#    __name__ 在这里会是 'py_ai_core.tools.general_tools'
logger = logging.getLogger(__name__)


@tool
async def get_current_weather(city: str, unit: str = "celsius") -> str:
    """获取指定城市的当前天气信息。

    这是工具的详细描述，可以有多行。
    第一行通常作为简短描述。

    :param city: 必要参数，需要获取天气的城市名称，例如 "北京"。
    :param unit: 可选参数，温度单位，可以是 "celsius" 或 "fahrenheit"，默认为 "celsius"。
    :return: 描述天气信息的字符串。
    """
    # 3. 在函数执行的开始记录日志，包含关键参数
    logger.info(
        "正在执行工具 [get_current_weather]，参数: city='%s', unit='%s'", city, unit
    )

    # 模拟实际的 API 调用。在真实场景中，这里会有网络请求。
    # 如果有错误，可以使用 logger.error() 或 logger.exception()
    try:
        # 这是一个模拟的返回结果
        weather_info = f"{city}的天气是晴朗, 30度 {unit}."
        logger.info("工具 [get_current_weather] 执行成功，返回: %s", weather_info)
        return weather_info
    except Exception as e:
        logger.exception("执行工具 [get_current_weather] 时发生未知错误。")
        # 向上抛出异常或返回一个错误信息
        return f"获取 {city} 天气时发生错误: {e}"


@tool
async def get_current_datetime() -> str:
    """返回当前服务器的日期和时间。

    这个工具非常简单，不需要任何参数。
    它会返回一个格式化好的字符串，表示当前的日期和时间。

    :return: 格式为 'YYYY-MM-DD HH:MM:SS' 的日期时间字符串。
    """
    logger.info("正在执行工具 [get_current_datetime]。")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.info("工具 [get_current_datetime] 执行成功，返回: %s", current_time)

    return current_time
