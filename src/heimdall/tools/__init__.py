# --- START OF FILE py_ai_core/tools/__init__.py ---

"""
工具包的初始化文件。

这里的核心作用是利用 "side-effect imports" (导入的副作用)。
当我们导入这个 `tools` 包时，Python会执行这个 `__init__.py` 文件。
通过在这里导入所有的工具模块（如 general_tools, math_tools），
我们确保了这些模块中的 `@tool` 装饰器能够被执行，
从而将所有工具自动注册到全局的 `tool_registry` 实例中。

这使得我们无需在应用的其他地方手动导入每一个工具文件，
让工具的注册过程变得自动化和集中化。
"""

from . import general_tools
from . import math_tools

# --- END OF FILE py_ai_core/tools/__init__.py ---
