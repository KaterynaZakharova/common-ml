"""Annotations analyse: quantity, bbox scale, position, distribution."""
from glob import glob
from typing import List, Tuple, Union, Set, Dict


def counter(
    path: str,
    filename: str = '*',
    classes: Union[Tuple[int], List[int], Set[int], Dict[int, int], tuple] = (),
) -> List[Tuple[int, int]]:
    """Counts each class amount in the annotations. If `classes` is
    given, returns 0's classes.

    Args:
        path (str): path to txt annotations
        filename (str, optional): check specific file. Defaults to '*' -
        check all files.
        classes (Union[Tuple[int], List[int], Set[int], Dict[int, int],
        tuple], optional): classes from config. Defaults to () - 0's
        classes will be ignored.

    Returns:
        List[Tuple[int, int]]: sorted by class a list of (class, amount)
        pairs
    """
    cnt = {cl: 0 for cl in classes}
    for txt_file in glob(f'{path}/{filename}.txt'):
        with open(txt_file, encoding='utf-8') as txt:
            while clss := txt.readline().split(' ', 1)[0]:
                if clss not in cnt:
                    cnt[clss] = -1
                cnt[clss] += 1
    return sorted(cnt.items())
