import matplotlib.pyplot as plt
from math import log
from typing import Union, Callable
import pandas as pd


def plot_histogram(df: pd.DataFrame, column_name:str, metric_column_name:str, funcs=list[Union[None, Callable]]):
    """Plot histograms for two slices of data.
    """
    # we assume the `column_name` has two unique values, we choose the first for A
    A = list(set(df[column_name].values))[0]
    # Create histograms
    # always do the identity
    funcs.append(lambda x: x)
    for func in funcs:
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
        ## TODO: make this write to filesystem
        plt.tight_layout()
        plt.show()