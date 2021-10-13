# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" `Utils` class providing generalized reusable functions for I/O, parsing, sorting, type conversions, etc.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
.. codeauthor:: Noussair Lazrak <lazrak.noussair@gmail.com>
"""
# Import python native libs
import json
import logging
import os
import shutil
import zipfile
from pathlib import Path
from urllib.parse import urlparse  # python3

# Import pypi libs
import requests
from tqdm import tqdm


class Utils():
    """Utils class."""

    def __init__(
            self,
    ):
        pass

    @staticmethod
    def mkdirs(path_as_string: str) -> bool:
        """ create folder in `path_as_string` if not already created. """

        if not os.path.exists(path_as_string):
            try:
                os.makedirs(path_as_string)
                return True
            except Exception as e:
                logging.error(f"Error while creating folders for path {path_as_string}: {e}")
                return False
        return True

    @staticmethod
    def is_file_located_or_downloaded(path_as_string: str, download_if_not_found: bool = True,
                                      download_link: str = None, is_new_download_forced: bool = False,
                                      allow_local_path_as_url: bool = True) -> bool:
        """ check if is file in `path_as_string` and optionally download the file (again). """

        if not path_as_string.is_file() or is_new_download_forced:
            if not download_if_not_found:
                # download_if_not_found is prioritized over is_new_download_forced in this case, as users likely
                # prefer to avoid automated downloads altogether when setting download_if_not_found to False.
                logging.warning(f"File {path_as_string} was not found ({not path_as_string.is_file()}) or download "
                                f"was forced ({is_new_download_forced}). However, downloading it from {download_link} "
                                f"was not allowed: download_if_not_found == {download_if_not_found}. This may cause an "
                                f"error, as the file might be outdated or missing, while being used in subsequent "
                                f"workflows.")
                return False
            else:
                try:
                    if allow_local_path_as_url and not Utils.is_url_valid(the_url=download_link):
                        shutil.copy2(src=download_link, dst=path_as_string)
                    else:
                        Utils.download_file(path_as_string=path_as_string, download_link=download_link)
                except Exception as e:
                    raise e
        return True

    @staticmethod
    def download_file(download_link: str, path_as_string: str):
        """ download a file using the `requests` lib and store in `path_as_string`"""

        logging.debug(f"Now downloading file {path_as_string} from {download_link} ...")
        try:
            response = requests.get(download_link, allow_redirects=True, stream=True)
            total_size_in_bytes = int(
                response.headers.get('content-length', 0))# / (32 * 1024)  # 32*1024 bytes received by requests.
            print(total_size_in_bytes)
            block_size = 1024
            progress_bar = tqdm(total=total_size_in_bytes, unit='B', unit_scale=True)
            progress_bar.set_description(f"Downloading {download_link}")
            with open(path_as_string, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
                logging.debug(
                    f"Received response {response}: Retrieved file from {download_link} and wrote it "
                    f"to {path_as_string}.")
        except Exception as e:
            logging.error(f"Error while trying to download/copy from {download_link} to {path_as_string}:{e}")
            raise e

    @staticmethod
    def read_in_json(path_as_string) -> dict:
        """ read a .json file and return as dict """

        try:
            with open(path_as_string) as f:
                json_file = json.load(f)
                return json_file
        except Exception as e:
            logging.error(f"Error while reading in json file from {path_as_string}: {e}")
            raise e

    @staticmethod
    def unzip_archive(source_path: Path, target_path_as_string: str = "./"):
        """ unzip a .zip archive in the `target_path_as_string` """

        try:
            with zipfile.ZipFile(source_path, 'r') as zip_ref:
                zip_ref.extractall(target_path_as_string)
        except Exception as e:
            logging.error(f"Error while unzipping {source_path}: {e}")
            raise e

    @staticmethod
    def dict_to_lowercase(target_dict: dict, string_conversion: bool = True) -> dict:
        """ transform values and keys in dict to lowercase, optionally with string conversion of the values.

        Warning: Does not convert nested dicts in the `target_dict`, but rather removes them from return object.
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

    @staticmethod
    def deep_get(base_dict: dict, key: str):
        """ Split the key by "." to get value in nested dictionary."""
        try:
            key_split = key.split(".")
            for key_ in key_split:
                base_dict = base_dict[key_]
            return base_dict
        except TypeError as e:
            logging.debug(
                f"No key ({key}) found in base_dict ({base_dict}) for this model. Fallback: Returning None.")
        return None

    @staticmethod
    def is_url_valid(the_url: str) -> bool:
        try:
            result = urlparse(the_url)
            # testing if both result.scheme and result.netloc are non-empty strings (empty strings evaluate to False).
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def order_dict_by_value(self, dict_list, key: str, order: str = "asc", sort_algorithm='bubbleSort') -> list:
        """ Sorting a list of dicts by the values of a specific key in the dict using a sorting algorithm.

        - This function is deprecated. You may use Python List sort() with key=lambda function instead.

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
