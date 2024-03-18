from datetime import datetime
from pathlib import Path
import yaml
import traceback
import pandas as pd
import logging
import sys
from pprint import pprint
import inspect

class Task:
    def __init__(self, task:str, logger:logging.Logger) -> None:
        self.logger = logger
        self.logger.info("----------------------------------------------------------------------------------------------------")
        self.TASK = task
        self.TIME_TAG = self.get_current_datetime()
        # file paths
        self.ROOT_PATH = Path(__file__).resolve().parent.parent
        self.PATH = {
            "LOG": (self.ROOT_PATH / 'log'),
            "DATA": (self.ROOT_PATH / 'data'),
            "TEMPLATES": (self.ROOT_PATH / 'templates'),
            "TASK_TEMPLATES": (self.ROOT_PATH / 'templates' / 'tasks'),
            "DATASET_TEMPLATES": (self.ROOT_PATH / 'templates' / 'datasets'),
            "CURRENT_RESULT": (self.ROOT_PATH / 'results' / self.TASK / self.TIME_TAG),
        }
        self.datasets = {}
        self.errors = {}
        self.task_yaml = self.load_task_template()

        # create paths
        self.create_paths()


    def safe_exit(self, source:str, msg:str, e:Exception=None):
        """
        safely exit the program and pprint the errors
        """
        self.logger.error(f"[{source}]: Critical error found, ending the program.")
        pprint(self.errors, width=100)
        sys.exit()


    def get_current_datetime(self):
        """
        get current date and time as string
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def create_paths(self):
        """
        Crate the necessary directories
        """
        for path in self.PATH.values():
            path.mkdir(parents=True, exist_ok=True)

    def load_task_template(self):
        """
        Load the task template, stop the program if this function fails.
        """
        try:
            self.logger.info(f"[src.Task.load_task_template]: Loading task template <{self.TASK}.yaml>")
            path = self.PATH["TASK_TEMPLATES"] / f"{self.TASK}.yaml"
            with open(path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            msg = f"Failed loading task template, please make sure the file <{self.TASK}.yaml> exists inside <{self.PATH['TASK_TEMPLATES']}> and in the correct format, double check if the name is correct, the task name has to be the same as the template file name."
            self.logger.error(f"[src.Task.load_task_template]: {msg}")
            self.logger.debug(f"[src.Task.load_task_template]: {e}\n**********\n{traceback.format_exc()}**********")
            self.errors["src.Task.load_task_template"] = msg
            self.safe_exit("src.Task.load_task_template", msg, e)

    def check_dataset_validation(self, template:str, data:dict):
        """
        Load template and datasets, check if the datasets are valid
        """
        self.load_data_template()
        self.load_data()
        self.errors['test'] = "test error"
        pass
    
    
    def prepare_datasets(self):
        """
        prepare the datasets from the data directory
        """
        self.logger.info(f"[src.Task.prepare_datasets]: Checking data for task <{self.TASK}>, found <{len(self.task_yaml['datasets'])}> templates.")
        for dataset in self.task_yaml["datasets"]:
            try:
                self.check_dataset_validation(dataset, self.task_yaml["datasets"][dataset])
            except Exception as e:
                msg = f"something went wrong while checking the dataset <{dataset}>"
                self.logger.error(f"[src.Task.prepare_datasets]: {msg}")
                self.logger.debug(f"[src.Task.prepare_datasets]: {e}\n**********\n{traceback.format_exc()}**********")
                self.errors["src.Task.prepare_datasets"] = msg
                self.safe_exit("src.Task.prepare_datasets", msg, e)
            else:
                self.logger.info(f"[src.Task.prepare_datasets]: Successfully checked template <{dataset}>, <{len(self.task_yaml['datasets'][dataset])}> files passed.")

        # error feedbacks
        if len(self.errors) > 0:
            self.safe_exit("src.Task.prepare_datasets", "something went wrong while preparing the datasets.")
