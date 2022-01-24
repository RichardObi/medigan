# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" `Utils` class providing generalized reusable functions for I/O, parsing, downloads, sorting, type conversions, etc.

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
from distutils.dir_util import copy_tree

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
    def mkdirs(path_as_string: str, is_exception_raised: bool = False) -> bool:
        """ create folder in `dest_path` if not already created. """

        if not os.path.exists(path_as_string):
            try:
                os.makedirs(path_as_string, exist_ok=True)
                return True
            except Exception as e:
                logging.error(f"Error while creating folders for path {path_as_string}: {e}")
                if is_exception_raised:
                    raise e
                return False
        return True

    @staticmethod
    def is_file_located_or_downloaded(dest_path: str, download_if_not_found: bool = True,
                                      download_link: str = None, is_new_download_forced: bool = False) -> bool:
        """ check if there is a file in `dest_path` and, if not, download the file (again) using `download_link`. """

        if not dest_path.is_file() or is_new_download_forced:
            if not download_if_not_found:
                # download_if_not_found is prioritized over is_new_download_forced in this case, as users likely
                # prefer to avoid automated downloads altogether when setting download_if_not_found to False.
                logging.warning(f"File {dest_path} was not found ({not dest_path.is_file()}) or download "
                                f"was forced ({is_new_download_forced}). However, downloading it from {download_link} "
                                f"was not allowed: download_if_not_found == {download_if_not_found}. This may cause an "
                                f"error, as the file might be outdated or missing, while being used in subsequent "
                                f"workflows.")
                return False
            else:
                Utils.download_file(dest_path=dest_path, download_link=download_link)
        return True



    @staticmethod
    def copy_(source_path: str, dest_path: str = "./"):
        """ copy either a file or folder from `source_path` to `dest_path` """

        try:
            if not Path(source_path).exists():
                # raise FileNotFound error here instead of warning?
                logging.error(
                    f"Error: Could not find a file/folder in: {source_path}. It was not copied to {dest_path}.")
            elif Path(source_path).is_file():
                logging.debug(f"Found a file in: {source_path}. Copying it now to {dest_path}.")
                shutil.copy2(src=source_path, dst=dest_path)
            elif Path(source_path).is_dir():
                logging.debug(f"Found a folder in: {source_path}. Copying it now to {dest_path}.")
                shutil.copytree(src=source_path, dst=dest_path)
        except Exception as e:
            logging.error(f"Error while copying {source_path} to {dest_path}: {e}")
            raise e

    @staticmethod
    def is_file_in(folder_path: str, filename: str):
        try:
            if Path(folder_path).is_dir() and Path(folder_path / filename).is_file():
                return True
        except Exception as e:
            logging.warning(f"File ({filename}) was not found in {folder_path}: {e}")
        finally:
            return False

    @staticmethod
    def download_file(download_link: str, dest_path: str, block_size: int = 1024):
        """ download a file using the `requests` lib and store in `dest_path`"""

        try:
            response = requests.get(url=download_link, allow_redirects=True, stream=True)
            total_size_in_bytes = int(
                response.headers.get('content-length', 0))  # / (32 * 1024)  # 32*1024 bytes received by requests.
            logging.warning(
                f"Now downloading model (size: {round(total_size_in_bytes/1048576, 2)}MB) from: {download_link}. "
                f"Will be stored in: {dest_path}")
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
            progress_bar.set_description(f"Downloading model (size: {round(total_size_in_bytes/1048576, 2)}MB)")
            with open(dest_path, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
                logging.debug(
                    f"Received response {response}: Retrieved file from {download_link} and wrote it "
                    f"to {dest_path}.")
            progress_bar.close()
        except (Exception, KeyboardInterrupt)as e:
            logging.error(f"Error: Interrupted while trying to download/copy from {download_link} to {dest_path}:{e}. "
                          f"Now collecting and deleting any partially downloaded files.")
            if os.path.isfile(dest_path):
                os.remove(dest_path)
            elif os.path.isdir(dest_path):
                shutil.rmtree(dest_path)
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
    def unzip_and_return_unzipped_path(package_path: str):
        """ if not already dir, unzip an archive with `Utils.unzip_archive`. Return path to unzipped dir/file """

        if Path(package_path).is_file() and package_path.endswith(".zip"):
            # Get the source_path without .zip extension to unzip.
            package_path_unzipped = package_path[0: -4]
            # We have a zip. Let's unzip and do the same operation (with new path)
            Utils.unzip_archive(source_path=package_path, target_path_as_string=package_path_unzipped)
            return package_path_unzipped
        elif Path(package_path).is_dir():
            logging.info(f"Your package path ({package_path}) does already point to a directory. It was not unzipped.")
            return package_path
        else:
            raise Exception(
                f"Your package path ({package_path}) does not point to a zip file nor directory. Please adjust and try again.")

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

    @staticmethod
    def store_dict_as(dictionary, extension: str = ".json", output_path: str = "config/",
                      filename: str = "metadata.json"):
        """ store a Python dictionary in file system as variable filetype."""

        if extension not in output_path:
            Utils.mkdirs(path_as_string=output_path)
            if extension not in filename:
                filename = filename + extension
            output_path = f'{output_path}/{filename}'
        json_object = json.dumps(dictionary, indent=4)
        with open(output_path, 'w') as outfile:
            outfile.write(json_object)

    @staticmethod
    def store(samples: list, output_path: str, filename: str = None, extension: str = 'png'):
        """ create folder in `output_path` and store generated `samples` there.

        -  This function is deprecated. medigan-models are responsible for storing generated samples. The reason is the
         difficulty in standardization of sample storage as each model has its own post-processing and interval mapping
         of images.

        """
        raise NotImplementedError
        # if extension is None: extension = 'png'
        # try:
        #    Utils.mkdirs(output_path, is_exception_raised=True)
        #    for idx, sample in enumerate(samples):
        #        if filename is not None:
        #            if len(samples) > 1:
        #                cv2.imwrite(f"{output_path}/{filename}_{idx}.{extension}", sample)
        #            else:
        #                cv2.imwrite(f"{output_path}/{filename}.{extension}", sample)
        #        else:
        #            cv2.imwrite(f"{output_path}/{idx}.{extension}", sample)
        # except Exception as e:
        #    raise e

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
