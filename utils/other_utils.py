import numpy as np
import pandas as pd

from Constants import Constants


def flatten_list(nested_list):
    """
    Recursively flattens a list of lists into a single list.

    :param nested_list: List with potentially nested lists
    :return: A flattened list
    """
    flattened = []
    for element in nested_list:
        if isinstance(element, list):
            flattened.extend(flatten_list(element))  # Recursively flatten sublists
        else:
            flattened.append(element)  # Append non-list elements directly
    return flattened


def clean_pandas_df(pandas_df: pd.DataFrame,
                    limit_cols: list = Constants.EXTRACT_COLUMN_KEYS,
                    values_to_clean: tuple = (np.nan, "-", "", None, "None", "no name found", "none")):
    cleaned_df = pandas_df[limit_cols]
    cleaned_df = cleaned_df.replace(to_replace=values_to_clean, value=pd.NA)
    cleaned_df = cleaned_df.dropna(how='all')
    cleaned_df = cleaned_df.replace(to_replace=pd.NA, value="")
    return cleaned_df
