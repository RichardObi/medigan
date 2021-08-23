# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" Utils class providing generalized reusable functions for I/O, parsing, sorting, type conversions, etc.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
.. codeauthor:: Noussair Lazrak <lazrak.noussair@gmail.com>
"""

import json
# Import python native libs
import os
import zipfile
from pathlib import Path

# Import pypi libs
import requests


class Utils():
    """Utils class."""

    def __init__(
            self,
    ):
        pass

    @staticmethod

    def mkdirs(path_as_string: str) -> bool:
        """ create folder in path_as_string if not already created. """

        if not os.path.exists(path_as_string):
            try:
                os.makedirs(path_as_string)
                return True
            except Exception as e:
                print(f"Error while creating folders for path {path_as_string}: {e}")
                return False
        return True

    @staticmethod
    def is_file_located_or_downloaded(path_as_string: str, download_if_not_found: bool = True,
                                      download_link: str = None, is_new_download_forced: bool = False) -> bool:
        """ check if is file in path_as_string and optionally download the file (again). """

        if not path_as_string.is_file() or is_new_download_forced:
            if not download_if_not_found:
                # download_if_not_found is prioritized over is is_new_download_forced in this case, as users likely
                # prefer to avoid automated downloads altogether when setting download_if_not_found to False.
                print(f"File {path_as_string} was not found ({not path_as_string.is_file()}) or download was forced "
                      f"({is_new_download_forced}). However, downloading it from {download_link} was not allowed: "
                      f"download_if_not_found == {download_if_not_found}.")
                return False
            else:
                try:
                    Utils.download_file(path_as_string=path_as_string, download_link=download_link)
                except Exception as e:
                    print(f"Error while trying to download file ({path_as_string}) from {download_link}: {e}")
                    return False
        return True

    @staticmethod
    def download_file(download_link: str, path_as_string: str):
        """ download a file using requests and store in path_as_string"""

        print(f"Now downloading file {path_as_string} from {download_link} ...")
        try:
            response = requests.get(download_link, allow_redirects=True)
            open(path_as_string, 'wb').write(response.content)
            print(
                f"Received response {response}: Retrieved file from {download_link} and wrote it to {path_as_string}.")
        except Exception as e:
            print(f"Error while downloading and storing file {path_as_string} from {download_link}: {e}")
            raise e

    @staticmethod
    def read_in_json(path_as_string) -> dict:
        """ read a .json file and return as dict """

        try:
            with open(path_as_string) as f:
                json_file = json.load(f)
                return json_file
        except Exception as e:
            print(f"Error while reading in json file from {path_as_string}: {e}")
            raise e

    @staticmethod
    def unzip_archive(source_path: Path, target_path_as_string: str = "./"):
        """ unzip a .zip archive in the target path """

        try:
            with zipfile.ZipFile(source_path, 'r') as zip_ref:
                zip_ref.extractall(target_path_as_string)
        except Exception as e:
            print(f"Error while unzipping {source_path}: {e}")
            raise e

    @staticmethod
    def dict_to_lowercase(target_dict: dict, string_conversion: bool = True) -> dict:
        """ transform values and keys in dict to lowercase, optionally with string conversion of the values.

        Warning: Does not convert nested dicts in the target_dict, but rather removes them from return object.
        """

        if string_conversion:
            # keys should always be strings per default. values might differ in type.
            return dict((k.lower(), str(v).lower()) for k, v in target_dict.items())
        else:
            return dict((k.lower(), v.lower()) for k, v in target_dict.items())

    @staticmethod
    def list_to_lowercase(target_list: list) -> list:
        """ string conversion and lower-casing of values in list.

        trade-off: String conversion for increased robustness > type failure detection
        """

        return [str(x).lower() for x in target_list]

    def deep_get(base_dict: dict, key: str):
        """ Split the key by "." to get value in nested dictionary."""

        key_split = key.split(".")
        for key_ in key_split:
            base_dict = base_dict[key_]
        return base_dict

    @staticmethod
    def order_dict_by_value(self, dict_list, key: str, order: str = "asc", sort_algorithm='bubbleSort') -> list:
        """ Sorting a list of dicts by the values of a specific key in the dict using a sorting algorithm.

            This function is deprecated. You may use Python List sort() with key=lambda function instead.
        """
        if sort_algorithm == 'bubbleSort':
            for i in range(len(dict_list)):
                for j in range(len(dict_list) - i - 1):
                    if dict_list[j][key] > dict_list[j + 1][key]:
                        # no need for a temp variable holder
                        dict_list[j][key], dict_list[j + 1][key] = dict_list[j + 1][key], dict_list[j][key]
        return dict_list

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
