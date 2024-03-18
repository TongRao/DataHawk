from datetime import datetime
from pathlib import Path
import yaml
import pandas as pd
from src.Task import Task
from src.Test import TestTask
import unittest
from pprint import pprint
from exzlogger import initialize_logger

if __name__ == '__main__':
    logger = initialize_logger(log_file="log/log.log")
    
    task = Task(task='sample_task', logger=logger)
    pprint(task.task_yaml)
    task.prepare_datasets()
    
    
    # unittest.main()