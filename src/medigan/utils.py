# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""
@author: Richard Osuala, Noussair Lazrak
BCN-AIM Lab 2021
Contact: richard.osuala@ub.edu
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
                                      download_link: str = None) -> bool:
        if not path_as_string.is_file():
            if not download_if_not_found:
                print(f"File {path_as_string} was not found, and downloading it from {download_link} was not allowed.")
                return False
            else:
                try:
                    Utils.download_file(path_as_string=path_as_string, download_link=download_link)
                except Exception as e:
                    return False
        return True

    @staticmethod
    def download_file(download_link: str, path_as_string: str):
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
        try:
            with open(path_as_string) as f:
                json_file = json.load(f)
                return json_file
        except Exception as e:
            print(f"Error while reading in json file from {path_as_string}: {e}")
            raise e

    @staticmethod
    def unzip_archive(source_path: Path, target_path_as_string: str = "./"):
        try:
            with zipfile.ZipFile(source_path, 'r') as zip_ref:
                zip_ref.extractall(target_path_as_string)
        except Exception as e:
            print(f"Error while unzipping {source_path}: {e}")
            raise e

    @staticmethod
    def dict_to_lowercase(target_dict: dict, string_conversion: bool = True) -> dict:
        # Warning: Does not convert nested dicts in the target_dict, but rather removes them from return object.
        if string_conversion:
            # keys should always be strings per default. values might differ in type.
            return dict((k.lower(), str(v).lower()) for k, v in target_dict.items())
        else:
            return dict((k.lower(), v.lower()) for k, v in target_dict.items())

    @staticmethod
    def list_to_lowercase(target_list: list) -> list:
        # trade-off: String conversion for increased robustness > type failure detection
        return [str(x).lower() for x in target_list]

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
