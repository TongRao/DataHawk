from pathlib import Path
import pandas as pd

def initialize_directories():
    """
    初始化所需的文件夹
    """
    # 基础文件夹
    ROOT_PATH = Path(__file__).resolve().parent
    paths = {
        "ROOT_PATH": ROOT_PATH,
        "DATA_PATH": ROOT_PATH / "data",
        "RESULT_ROOT_PATH": ROOT_PATH / "result",
        "TEMPLATE_PATH": ROOT_PATH / "templates",
        "LOG_PATH": ROOT_PATH / "log",
        "CONFIG_PATH": ROOT_PATH / "config",
    }
    # 创建文件夹
    for path in paths:
        if path.endswith("_PATH"):
            paths[path].mkdir(exist_ok=True, parents=True)
    return paths

def get_general_column_type(dtype):
    """
    Define the general type of a column based on its dtype
    """
    if pd.api.types.is_numeric_dtype(dtype):
        return 'numeric'
    elif pd.api.types.is_string_dtype(dtype):
        return 'text'
    elif pd.api.types.is_bool_dtype(dtype):
        return 'bool'
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return 'datetime'
    else:
        return 'unknown'
    