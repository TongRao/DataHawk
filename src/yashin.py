import pandas as pd
import toml, os
from pathlib import Path
from src.utils import initialize_directories, get_general_column_type

class LoadDataError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class LoadTemplateError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class CreateTemplateError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class DoorKeeperValidationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class DoorKeeper:
    def __init__(self, data_source, template_name, force_create=False, allow_empty_cols=[], required_cols=[], col_aliases={}) -> None:
        self.data_source = data_source
        self.template_name = template_name
        self.allow_empty_cols = allow_empty_cols
        self.required_cols = required_cols
        self.col_aliases = col_aliases
        
        # init run
        self.data_origin = self.load_data()
        self.data = self.data_origin.copy()
        self.template_list = self._load_template_list()
        
        # check if data template exists, if not create one
        if self.template_name in self.template_list['templates'] and not force_create:
            self.data_template = self.load_data_template()
        else:
            self.data_template = self.create_template()

        # validation
        self._validate_data()

    def __call__(self):
        return self.data

    # ---------------------------------------------------------------------------------------------------- #
    def _check_template_list_exists(self):
        """
        Check if the template list exists
        """
        if not os.path.exists(Path("templates") / "template_list.toml"):
            template_list = {"templates": []}
            with open(Path("templates") / "template_list.toml", "w") as f:
                toml.dump(template_list, f)


    def _load_template_list(self):
        """
        TODO: Add Exceptions
        """
        self._check_template_list_exists()
        with open(Path("templates") / "template_list.toml", "r") as f:
            template_list = toml.load(f)
        return template_list
    

    def _get_template_list_value_by_path(self):
        """
        Get the value of a key in the template list
        TODO: Add Exceptions
        """
        keys = self.data_template.split('.')
        for key in keys:
            result = self.data_origin[key]
        return result
    

    def supported_templates(self):
        """
        Return a list of supported templates
        """
        print(self.template_list['templates'])
        

    def load_data(self):
        """
        Load data from a csv or excel file
        """
        try:
            if ".csv" in self.data_source:
                data = pd.read_csv(self.data_source)
            else:
                data = pd.read_excel(self.data_source)
            return data
        except Exception as e:
            raise LoadDataError(f"Error loading data: {e}")
        

    def load_data_template(self):
        """
        Load data template from a toml file if it exists
        """
        try:
            with open(Path("templates") / f"{self.template_name}.toml", "r") as f:
                template = toml.load(f)
            return template
        except Exception as e:
            raise LoadTemplateError(f"Error loading data template: {e}")
        

    def create_template(self):
        """
        Create a template from the data source
        """
        try:
            template_rules = {}

            for col in self.data_origin.columns:
                col_info = {}
                col_info['alias'] = list(set(self.col_aliases.get(col, [col]) + [col]))
                col_info['dtype'] = get_general_column_type(self.data_origin[col].dtype)
                col_info['allow_null'] = col in self.allow_empty_cols
                col_info['required'] = col in self.required_cols
                template_rules[col] = col_info

            # add current tepmplate to template list
            self.template_list['templates'].append(self.template_name)
            with open(Path("templates") / "template_list.toml", 'w') as f:
                toml.dump(self.template_list, f)

            # Convert the template dictionary to TOML format and write to file
            with open(Path("templates") / f"{self.template_name}.toml", 'w') as toml_file:
                toml.dump(template_rules, toml_file)
            return template_rules
        except Exception as e:
            raise CreateTemplateError(f"Error creating data template: {e}")
        
    
    def _validate_data(self):
        """
        Validate the data against the template
        """
        validation_errors = []

        for col, col_info in self.data_template.items():
            # 用标准列名替换所有别名
            alias_mapping = {}
            aliases = col_info.get('alias', [])
            for alias in aliases:
                alias_mapping[alias] = col
            alias_mapping[col] = col
            self.data = self.data.rename(columns=alias_mapping)

            # 检查列是否存在
            if col not in self.data.columns:
                if col_info.get('required', False):
                    validation_errors.append(f"Missing required column: {col}")
                continue

            # 检查数据类型
            general_type = get_general_column_type(self.data[col].dtype)
            if general_type != col_info['dtype']:
                validation_errors.append(f"Column <{col}> has wrong type: expected <{col_info['dtype']}>, found <{general_type}>")

            # 检查空值
            if not col_info['allow_null'] and self.data[col].isnull().any():
                validation_errors.append(f"Column <{col}> contains null values but is not allowed")

        # 检查是否有多余的列
        for col in self.data.columns:
            if col not in self.data_template:
                validation_errors.append(f"Unexpected column: {col}")
        
        # print validation_errors
        if validation_errors:
            raise DoorKeeperValidationError(f"Invalid data <{self.data_source}> with template <{self.template_name}>: \n - " + "\n - ".join(validation_errors))
        else:
            print("Data is valid!")

