import unittest
from pathlib import Path
import os
import pandas as pd
import yaml
from src.Task import Task

class TestTask(unittest.TestCase):
    def setUp(self):
        self.task = Task('test_task')

    def test_get_current_datetime(self):
        self.assertIsInstance(self.task.get_current_datetime(), str)

    def test_create_paths(self):
        self.task.create_paths()
        for path in self.task.PATH.values():
            self.assertTrue(path.exists())

    def test_load_task_template(self):
        # Create a dummy yaml file for testing
        with open(self.task.PATH["TASK_TEMPLATES"] / f'{self.task.TASK}.yaml', 'w') as file:
            yaml.dump({"key": "value"}, file)

        data = self.task.load_task_template()
        self.assertEqual(data, {"key": "value"})

    def test_load_datasets(self):
        # Create a dummy csv file for testing
        df = pd.DataFrame({"column1": [1, 2, 3]})
        df.to_csv(self.task.PATH["DATA"] / f'{self.task.TASK}.csv', index=False)

        self.task.datasets = {f'{self.task.TASK}.csv': None}
        self.task.load_datasets()
        pd.testing.assert_frame_equal(self.task.datasets[f'{self.task.TASK}.csv'], df)
        