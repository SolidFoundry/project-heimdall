# py_ai_core/tools/math_tools.py

import logging
import math
from .registry import tool

logger = logging.getLogger(__name__)

# 一个安全的数学函数和常量的白名单
SAFE_MATH_OPS = {
    "abs": abs,
    "acos": math.acos,
    "asin": math.asin,
    "atan": math.atan,
    "atan2": math.atan2,
    "ceil": math.ceil,
    "cos": math.cos,
    "cosh": math.cosh,
    "degrees": math.degrees,
    "exp": math.exp,
    "fabs": math.fabs,
    "floor": math.floor,
    "fmod": math.fmod,
    "frexp": math.frexp,
    "hypot": math.hypot,
    "ldexp": math.ldexp,
    "log": math.log,
    "log10": math.log10,
    "modf": math.modf,
    "pow": math.pow,
    "radians": math.radians,
    "sin": math.sin,
    "sinh": math.sinh,
    "sqrt": math.sqrt,
    "tan": math.tan,
    "tanh": math.tanh,
    "pi": math.pi,
    "e": math.e,
}


@tool
async def calculate(expression: str) -> str:
    """
    一个安全的计算器，用于执行数学表达式。
    你可以用它来做加减乘除、乘方、开方等运算。
    例如: "10 * (3 + 5) / 2", "pow(2, 10)", "sqrt(144)".

    :param expression: 一个字符串形式的数学表达式。
    :return: 计算结果的字符串，或在出错时返回错误信息。
    """
    logger.info("正在执行工具 [calculate]，表达式: '%s'", expression)

    try:
        # 使用一个安全的 eval 环境，只允许白名单中的数学运算
        # 这是比直接使用 eval() 更安全的做法
        result = eval(expression, {"__builtins__": None}, SAFE_MATH_OPS)

        # 将结果转换为字符串返回
        result_str = str(result)
        logger.info("工具 [calculate] 执行成功，返回: %s", result_str)
        return result_str

    except Exception as e:
        # 捕获任何可能的错误，如语法错误、除零错误等
        error_message = f"计算表达式 '{expression}' 时发生错误: {e}"
        logger.error(error_message, exc_info=True)
        return error_message
