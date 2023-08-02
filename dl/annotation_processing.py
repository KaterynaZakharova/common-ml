"""Work with annotations any format"""
import json
import os
from glob import glob
from typing import Dict, List, Tuple, Union

from helpers.path_and_files_processing import (
    combine_path,
    create_dir,
    get_filename,
    get_files,
)

YOLO_FORMAT = '%(class_id)s %(x)s %(y)s %(w)s %(h)s'


def bbox2yolo(
    width: int, height: int, xmin: int, ymin: int, xmax: int, ymax: int
) -> Tuple[float, float, float, float]:
    """Convert a bounding box (rectangle) to the YOLO format.

    Args:
        width (int): image width
        height (int): image height
        xmin (int): left point (x min)
        ymin (int): top point (y min)
        xmax (int): right point (x max)
        ymax (int): bottom point (y max)

    Returns:
        Tuple[float, float, float, float]: scaled (YOLO) coordinates:
        centre points (x, y), rectangle size (width, height)
    """
    dw = 1 / width
    dh = 1 / height
    x = ((xmin + xmax) / 2) * dw
    y = ((ymin + ymax) / 2) * dh
    w = (xmax - xmin) * dw
    h = (ymax - ymin) * dh
    return x, y, w, h


def yolo2bbox(x: float, y: float, w: float, h: float) -> Tuple[int, int, int, int]:
    """Convert scaled (YOLO) coordinates to a bounding box (rectangle).

    Args:
        x (float): centre point X
        y (float): centre point Y
        w (float): rectangle width
        h (float): rectangle height

    Returns:
        Tuple[int, int, int, int]: top left point (min x, y),
        bottom right point (max x, y)
    """
    xmin, ymin = int(x - w / 2), int(y - h / 2)
    xmax, ymax = int(x + w / 2), int(y + h / 2)
    return xmin, ymin, xmax, ymax


class TXTAnnotations:
    """Process txt (YOLO) annotations files."""

    def __init__(
        self,
        images_path: str,
        txt_path: str = f'{os.getcwd()}/txt_annotations/',
        classes_config: Union[tuple, Tuple[int], List[int]] = (),
    ) -> None:
        """Based on images' filenames process txt files.

        Args:
            images_path (str): path to images
            txt_path (str, optional): path to txt annotations. Defaults
            to f'{os.getcwd()}/txt_annotations/'.
            classes_config (Union[tuple, Tuple[int], List[int]]): a
            sorted list of classes. Defaults to ().
        """
        self.images_path = images_path
        self.txt_path = create_dir(txt_path)
        self.classes_config = classes_config

    def empty_txt(self, filename: str = '*') -> None:
        """Create new empty (rewrite old) txt annotations to all
        pictures.

        If `filename` was passed, the function will work only with that
        file.

        Args:
            filename (str, optional): file name without its path.
            Defaults to *.
        """
        for txt in get_files(self.txt_path, filename):
            open(txt, 'w', encoding='utf-8').close()

    def add_txt(self, filename: str = '*') -> None:
        """Add empty txt annotations to the pictures with no annotations.

        If `filename` was passed, the function will work only for that
        picture.

        Args:
            filename (str, optional): file name without its path.
            Defaults to *.
        """
        for img in get_files(self.images_path, filename):
            txt_file = combine_path(self.txt_path, get_filename(img))
            if not os.path.exists(txt_file):
                open(txt_file, 'w+', encoding='utf-8').close()

    def update_classes(self, to_remove: Union[Tuple[int], List[int]]) -> Dict[int, int]:
        """Shifts untouched classes to start from 0.

        Example:
        >>> Input:
            - 2 0.5 0.5 0.1 0.1 <
            - 1 0.4 0.3 0.3 0.2
            - 0 0.2 0.1 0.4 0.5
        >>> to_remove = (0, 1)
        >>> Output:
            - 0 0.5 0.5 0.1 0.1

        >>> Input:
            - 2 0.5 0.5 0.1 0.1
            - 1 0.4 0.3 0.3 0.2
            - 0 0.2 0.1 0.4 0.5 <
        >>> to_remove = (2, 1)
        >>> Output:
            - 0 0.2 0.1 0.4 0.5

        Args:
            to_remove (Union[Tuple[int], List[int]]): list all classes
            to remove. Should be iterable and sorted.

        Raises:
            ValueError: `self.classes_config` should be passed before
            attempting classes removing. A full list of used classes is
            required to shift classes correctly.

        Returns:
            Dict[int, int]: updated dictionary with old classes are keys,
            shifted classes are values
        """
        if not self.classes_config:
            raise ValueError('Classes config was not passed.')

        keep = {}
        shift = 0

        for old_class in self.classes_config:
            if old_class in to_remove:
                shift += 1

            elif old_class not in keep:
                keep[old_class] = old_class - shift
        return keep

    def remove_class(
        self, to_remove: Union[Tuple[int], List[int]], filename: str = '*'
    ) -> None:
        """Remove class(es) from annotations.

        Args:
            to_remove (Union[Tuple[int], List[int]]): list all classes
            to remove. Should be iterable and sorted.
            filename (str, optional): remove class(es) for specific
            file. Defaults to '*'.
        """
        keep = self.update_classes(to_remove)

        for txt in get_files(self.txt_path, filename):
            with open(txt, "r+", encoding='utf-8') as txt:
                new_txt = txt.readlines()
                txt.seek(0)
                for line in new_txt:
                    cur_class, line_wo_class = line.split(' ', 1)
                    cur_class = int(cur_class)
                    if cur_class not in to_remove:
                        txt.write(f'{keep[cur_class]} {line_wo_class}')
                txt.truncate()

    def replace_classes(
        self, to_replace_with: Dict[int, int], filename: str = '*'
    ) -> None:
        """Replace classes according to a new config - `to_replace_with`.

        Args:
            to_replace_with (Dict[int, int]): a new classes config,
            where keys are old classes and values are new ones.
            filename (str, optional): remove class(es) for specific
            file. Defaults to '*'.
        """
        self.classes_config = to_replace_with

        for txt in get_files(self.txt_path, filename):
            with open(txt, "r+", encoding='utf-8') as txt:
                new_txt = txt.readlines()
                txt.seek(0)
                for line in new_txt:
                    cur_class, line_wo_class = line.split(' ', 1)
                    cur_class = int(cur_class)
                    txt.write(f'{to_replace_with[cur_class]} {line_wo_class}')
                txt.truncate()


class JSON2TXT(TXTAnnotations):
    """Converts JSON annotations to the TXT (YOLO) format"""

    def __init__(
        self,
        json_path: str,
        images_path: str,
        map_config: Dict[int, int],
        txt_path: str = f'{os.getcwd()}/txt_annotations/',
    ) -> None:
        """Get data from json file and convert it to the txt format.

        Args:
            json_path (str): path to json annotations
            images_path (str): path to images
            map_config (Dict[int, int]): config to replace json classes
            with txt ones.
            txt_path (str, optional): path to txt annotations. Defaults
            to f'{os.getcwd()}/txt_annotations/'.
        """
        super().__init__(images_path, txt_path)
        self.json_path = json_path
        self.map_config = map_config

    def map_class(self, class_id: int) -> int:
        """Map JSON class Ids to YOLO classes

        Args:
            class_id (int): JSON class Id

        Returns:
            int: YOLO class number
        """
        return self.map_config[class_id]

    def json2txt(self, filename: str = '*') -> None:
        """Convert JSON annotations to txt.

        Args:
            filename (str, optional): name of the file to create txt
            annotations for. Defaults to '*'.
        """
        for json_file in glob(f'{self.json_path}/{filename}'):
            txt_file = combine_path(self.txt_path, get_filename(json_file))
            with open(json_file, 'r', encoding='utf-8') as js, open(
                txt_file, 'w+', encoding='utf-8'
            ) as txt:
                data = json.load(js)

                image_size = data['size']
                width, height = image_size['width'], image_size['height']

                for obj in data['objects']:
                    points = obj['points']['exterior']
                    xmin, ymin = points[0]
                    xmax, ymax = points[-1]

                    x, y, w, h = bbox2yolo(width, height, xmin, ymin, xmax, ymax)
                    class_id = self.map_class(obj['classId'])

                    txt.write(f'{YOLO_FORMAT % locals()}\n')
