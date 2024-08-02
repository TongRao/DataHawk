from pathlib import Path
import pandas as pd

def initialize_directories(root):
    """
    初始化所需的文件夹
    """
    # 基础文件夹
    ROOT_PATH = Path(root).resolve().parent
    ROOT_PATH = ROOT_PATH.parent if ROOT_PATH.name == "src" else ROOT_PATH

    dirs = {
        "root": ROOT_PATH,
        "data": ROOT_PATH / "data",
        "result": ROOT_PATH / "result",
        "yashin": ROOT_PATH / "yashin",
        "log": ROOT_PATH / "log",
        "test": ROOT_PATH / "test",
    }
    # 创建文件夹
    for path in dirs:
        dirs[path].mkdir(exist_ok=True, parents=True)
    return dirs

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
    