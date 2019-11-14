"""CLI."""

import importlib

from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import Union

import click
import pandas as pd
import yaml

from joblib import dump


@click.group()
def optgbm() -> None:
    """Run optgbm."""


@optgbm.command()
@click.argument('recipe_path')
def train(recipe_path: str) -> None:
    """Train the model with a recipe."""
    trainer = Trainer()

    trainer.train(recipe_path)


class Dataset(object):
    """Dataset."""

    def __init__(
        self,
        data: str,
        label: str = None,
        dtype: Optional[Dict[str, Union[Type, str]]] = None,
        index_col: Union[int, List[int], List[str], str] = None
    ):
        self.data = data
        self.label = label
        self.dtype = dtype
        self.index_col = index_col

        self._data = pd.read_csv(data, dtype=dtype, index_col=index_col)

    def get_data(self) -> pd.DataFrame:
        """Get the data of the dataset."""
        if self.label is None:
            return self._data

        return self._data.drop(columns=self.label)

    def get_label(self) -> Optional[pd.Series]:
        """Get the label of the dataset."""
        if self.label is None:
            return None

        return self._data[self.label]


class Trainer(object):
    """Trainer."""

    def train(self, recipe_path: str) -> None:
        """Train the model with a recipe."""
        with open(recipe_path, 'r') as f:
            content = yaml.load(f)

        dtype = content.get('dtype')
        index_col = content.get('index_col')
        params = content.get('params', {})
        fit_params = content.get('fit_params', {})

        dataset = Dataset(
            content['data_path'],
            label=content['label_col'],
            dtype=dtype,
            index_col=index_col
        )
        data = dataset.get_data()
        label = dataset.get_label()

        module_name, class_name = content['model_source'].rsplit(
            '.',
            maxsplit=1
        )
        module = importlib.import_module(module_name)
        klass = getattr(module, class_name)
        model = klass(**params)

        model.fit(data, label, **fit_params)

        dump(model, content['model_path'])
