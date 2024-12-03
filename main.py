import pandas as pd
import toml
import os
from pathlib import Path
from src.utils import get_general_column_type
import sys


def load_data(data_path: str|Path) -> pd.DataFrame:
    """
    Load data from a csv or excel file

    Parameters:
        - data_path <str|Path>: full data path

    Returns:
        - data <pd.DataFrame>: data loaded from the file
    """
    try:
        if ".csv" in str(data_path):
            data = pd.read_csv(data_path)
        elif ".xlsx" in str(data_path):
            data = pd.read_excel(data_path)
        else:
            sys.exit("Data file must be in csv or excel format!")
        return data
    except Exception as e:
        sys.exit(f"[data_loader]: Failed to load data\n-----\n{e}\n-----")


def load_template(task: str, template_dir:Path) -> dict:
    """
    Load data template from a toml file if it exists

    Parameters:
        - task <str>: The task name
        - template_dir <Path>: The directory to save the template

    Returns:
        - template <dict>: The template dictionary
    """
    try:
        with open(template_dir / f"{task}.toml", "r") as f:
            template = toml.load(f)
        return template
    except Exception as e:
        sys.exit(f"[template_loader]: Failed to load template\n-----\n{e}\n-----")


def create_template(data: pd.DataFrame, task: str, template_dir:str|Path, override: bool=False) -> dict:
    """
    Create a template from the data source

    Parameters:
        - data <DataFrame>: The data source
        - task <str>: The task name
        - template_dir <str|Path>: The directory to save the template
        - override <bool>: Whether to override the existing template

    Returns:
        - template_rules <dict>: The template dictionary
    """
    try:
        template_rules = {
            "title": task,  # Add metadata
            "description": f"Template for {task}",
            "source": "generated",
            "columns": {}  # Nested table structure
        }

        for col in data.columns:
            col_info = {}
            col_info['alias'] = [col]
            col_info['dtype'] = get_general_column_type(data[col].dtype)
            col_info['allow_null'] = False
            col_info['required'] = True
            template_rules["columns"][col] = col_info

        # Convert the template dictionary to TOML format and write to file
        template_path = template_dir / f"{task}.toml"
        if template_path.exists() and not override:
            print(f"[template_creator]: Template already exists at <{template_path}>")
            template_rules = toml.load(template_path)
            return template_rules
        with open(template_path, 'w') as toml_file:
            toml.dump(template_rules, toml_file)
            print(f"[template_creator]: Template created at <{template_path}>")
        return template_rules
    except Exception as e:
        sys.exit(f"[template_creator]: Failed to create template\n-----\n{e}\n-----")


def validate(data, template, fix_errors=False, language='en'):
    """
    Validate the data against the template

    Parameters:
        - data <pd.DataFrame>: The data to validate
        - template <dict>: The template to validate against
        - fix_errors <bool>: Whether to fix the errors
        - language <str>: The language to use for error messages

    Returns:
        - data <pd.DataFrame>: The data after fixing errors
        - validation_errors <list>: List of validation errors
    """
    validation_errors = []
    error_messages = {
        "en": {
            "null_values": "Column <{}> contains null values but is not allowed",
            "missing_column": "Column <{}> is missing but is required",
            "wrong_type": "Column <{}> has wrong type, expected <{}>, found <{}>",
            "unexpected_column": "Column <{}> is not expected"
        },
        "ch": {
            "null_values": "<{}>列包含空值，根据规则该列不允许存在空值",
            "missing_column": "<{}>列缺失，根据规则该列必须存在",
            "wrong_type": "<{}>列类型错误，根据规则应为<{}>, 实际为<{}>",
            "unexpected_column": "<{}>列不应存在"
        }
    }

    for col, col_info in template.get('columns', {}).items():
        # replace column aliases with standard column names
        alias_mapping = {}
        aliases = col_info.get('alias', [])
        for alias in aliases:
            alias_mapping[alias] = col
        alias_mapping[col] = col
        data = data.rename(columns=alias_mapping)

        # check for missing columns
        if col not in data.columns:
            if col_info.get('required', False):
                validation_errors.append(error_messages[language]['missing_column'].format(col))
            continue

        # check for columns type
        general_type = get_general_column_type(data[col].dtype)
        if general_type != col_info['dtype']:
            validation_errors.append(error_messages[language]['wrong_type'].format(col, col_info['dtype'], general_type))

        # check for null values
        if not col_info['allow_null'] and data[col].isnull().any():
            validation_errors.append(error_messages[language]['null_values'].format(col))

    # check for unexpected columns
    for col in data.columns:
        if col not in template.get('columns', {}):
            validation_errors.append(error_messages[language]['unexpected_column'].format(col))
    return validation_errors


def informer(errors: list, language: str='en'):
    """
    Print validation errors

    Parameters:
        - errors <list>: List of validation errors
    """
    if errors:
        print("[informer]: Data is invalid:") if language == 'en' else print("[informer]: 数据校验失败:")
        print("**********")
        print(" - " + "\n - ".join(errors))
        print("**********")
    else:
        print("[informer]: Data is valid!") if language == 'en' else print("[informer]: 数据校验通过!")


def hawk_check(data_path: str|Path, task: str, template_dir: str|Path=Path('datahawk'), fix_errors: bool=False, override: bool=False, language: str='en'):
    """
    Main function to load data, create template, validate data and save template

    Parameters:
        - data_path <str|Path>: The data source path
        - task <str>: The task name
        - template_dir <str|Path>: The directory to save the template
        - TODO fix_errors <bool>: Whether to fix the errors
        - override <bool>: Whether to override the existing template
        - language <str>: The language to use for error messages

    Returns:
        - data <pd.DataFrame>: The data after fixing errors
        - validation_errors <list>: List of validation errors
    """
    # check path type, convert string into Path
    if isinstance(data_path, str):
        data_path = Path(data_path)
    if isinstance(template_dir, str):
        template_dir = Path(template_dir)

    data = load_data(data_path)

    # check if template exists, if not create one else load the existing template
    template_path = template_dir / f"{task}.toml"
    template = create_template(data, task, template_dir, override)
    template = load_template(task, template_dir)

    # validate data
    errors = validate(data, template, fix_errors, language)

    # print validation errors
    informer(errors, language)


# if __name__ == "__main__":
#     data_path = Path("test") / "test2.csv"
#     task = "test2"
#     hawk_check(data_path=data_path, task=task, template_dir="datahawk", fix_errors=False, override=False, language='en')
