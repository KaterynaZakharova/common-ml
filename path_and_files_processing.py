"""Use directory structure and path processing"""
from glob import glob
import os
from pathlib import Path
from typing import List, Union


def create_dir(path: str) -> str:
    """Creates directory based on path.

    Args:
        path (str): full path (absolute or relative) to a new directory

    Returns:
        str: same inputted path
    """
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def get_filename(path: str) -> str:
    """Returns filename without its extension.

    Args:
        path (str): path to file

    Returns:
        str: filename
    """
    return os.path.split(path)[-1].split('.', 1)[0]


def combine_path(
    folder: str, filename: str, extension: Union[str, None] = 'txt'
) -> str:
    """Combine `folder`, `filename` and `extension` to get full path to
    the expected file.

    Used to create empty files, or find same-name-different-extension
    files.

    Args:
        folder (str): folder path
        filename (str): filename
        extension (Union[str, None], optional): file extension. `None`
        is expected if need to keep original extension. Defaults to
        'txt'.

    Returns:
        str: full path
    """
    if not extension:  # if filename have to keep its extension
        return f'{folder}/{filename}'
    return f'{folder}/{filename}.{extension}'


def get_files(folder: str, filename: str) -> List[str]:
    """List all files using expression

    Args:
        folder (str): folder path
        filename (str): filename

    Returns:
        List[str]: path to files
    """
    return glob(combine_path(folder, filename, None))
