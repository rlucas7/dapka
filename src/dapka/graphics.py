import logging
import matplotlib.pyplot as plt
from math import log
from typing import Union, Callable
import pandas as pd


logger = logging.getLogger(__name__)


def plot_histogram(df: pd.DataFrame, column_name:str, metric_column_name:str, funcs=list[Union[None, Callable]], savefig:bool=False) -> None:
    """Plot histograms for two slices of data.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        column_name (str): The name of the column to slice the data.
        metric_column_name (str): The name of the metric column to plot.
        funcs (list[Union[None, Callable]]): List of functions to apply to the metric values.
        savefig (bool): If True, saves the figure instead of showing it.

    Returns:
        None: Displays or saves the histogram plots.
    """
    # we assume the `column_name` has two unique values, we choose the first for A
    A = list(set(df[column_name].values))[0]
    # Create histograms
    # always do the identity function as one of the funcs
    funcs.append(lambda x: x)
    for func in funcs:
        logger.info(f"Plotting histograms for {column_name} and {metric_column_name} with function: {func.__name__}")
        data_A = [func(float(val)) for val in df[df[column_name]==A][metric_column_name].dropna().values]
        data_B = [func(float(val)) for val in df[df[column_name]!=A][metric_column_name].dropna().values]
        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 6))
        x_label, y_label = f"Value of {func.__name__}", f"Frequency of {func.__name__}"
        axes[0].hist(data_A, bins=30, edgecolor='black', alpha=0.7, density=True)
        axes[0].set_title(f"Histogram of {A}")
        axes[0].set_xlabel(x_label)
        axes[0].set_ylabel(y_label)
        axes[1].hist(data_B, bins=30, edgecolor='black', alpha=0.7, color='orange', density=True)
        axes[1].set_title(f"Histogram of not {A} values")
        axes[1].set_xlabel(x_label)
        axes[1].set_ylabel(y_label)
        plt.tight_layout()
        if savefig:
            plt.savefig(f"histogram_{func.__name__}_by_{column_name}_metric_{metric_column_name}.png")
        else:
            plt.show()
        plt.close(fig)
        logger.info(f"Plotting histograms for {column_name} and {metric_column_name} with function: {func.__name__}")