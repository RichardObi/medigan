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
from distutils.dir_util import copy_tree
from pathlib import Path
from urllib.parse import urlparse  # python3

# Import pypi libs
import requests
from tqdm import tqdm
import numpy as np


class Utils:
    """Utils class."""

    def __init__(
        self,
    ):
        pass

    @staticmethod
    def mkdirs(path_as_string: str) -> bool:
        """create folder in `path_as_string` if not already created."""

        if not os.path.exists(path_as_string):
            try:
                os.makedirs(path_as_string)
                return True
            except Exception as e:
                logging.error(
                    f"Error while creating folders for path {path_as_string}: {e}"
                )
                return False
        return True

    @staticmethod
    def is_file_located_or_downloaded(
        path_as_string: str,
        download_if_not_found: bool = True,
        download_link: str = None,
        is_new_download_forced: bool = False,
        allow_local_path_as_url: bool = True,
    ) -> bool:
        """check if is file in `path_as_string` and optionally download the file (again)."""

        if not path_as_string.is_file() or is_new_download_forced:
            if not download_if_not_found:
                # download_if_not_found is prioritized over is_new_download_forced in this case, as users likely
                # prefer to avoid automated downloads altogether when setting download_if_not_found to False.
                logging.warning(
                    f"File {path_as_string} was not found ({not path_as_string.is_file()}) or download "
                    f"was forced ({is_new_download_forced}). However, downloading it from {download_link} "
                    f"was not allowed: download_if_not_found == {download_if_not_found}. This may cause an "
                    f"error, as the file might be outdated or missing, while being used in subsequent "
                    f"workflows."
                )
                return False
            else:
                try:
                    if allow_local_path_as_url and not Utils.is_url_valid(
                        the_url=download_link
                    ):
                        Utils.copy(
                            source_path=download_link,
                            target_path=os.path.split(path_as_string)[0],
                        )
                    else:
                        Utils.download_file(
                            path_as_string=path_as_string, download_link=download_link
                        )
                except Exception as e:
                    raise e
        return True

    @staticmethod
    def download_file(download_link: str, path_as_string: str):
        """download a file using the `requests` lib and store in `path_as_string`"""

        logging.debug(f"Now downloading file {path_as_string} from {download_link} ...")
        try:
            for i in range(10):
                response = requests.get(
                    download_link, allow_redirects=True, stream=True
                )
                total_size_in_bytes = int(
                    response.headers.get("content-length", 0)
                )  # / (32 * 1024)  # 32*1024 bytes received by requests.
                logging.debug(total_size_in_bytes)
                block_size = 1024
                progress_bar = tqdm(
                    total=total_size_in_bytes, unit="B", unit_scale=True
                )
                progress_bar.set_description(f"Downloading {download_link}")
                with open(path_as_string, "wb") as file:
                    for data in response.iter_content(block_size):
                        progress_bar.update(len(data))
                        file.write(data)
                    logging.debug(
                        f"Received response {response}: Retrieved file from {download_link} and wrote it "
                        f"to {path_as_string}."
                    )

                try:
                    zipfile.ZipFile(path_as_string, "r")
                    break
                except Exception as e:
                    logging.debug(
                        f"Download failed. Retrying download from {download_link}"
                    )

        except Exception as e:
            logging.error(
                f"Error while trying to download/copy from {download_link} to {path_as_string}:{e}"
            )
            raise e

    @staticmethod
    def read_in_json(path_as_string) -> dict:
        """read a .json file and return as dict"""

        try:
            with open(path_as_string) as f:
                json_file = json.load(f)
                return json_file
        except Exception as e:
            logging.error(
                f"Error while reading in json file from {path_as_string}: {e}"
            )
            raise e

    @staticmethod
    def unzip_archive(source_path: Path, target_path: str = "./"):
        """unzip a .zip archive in the `target_path`"""

        try:
            with zipfile.ZipFile(source_path, "r") as zip_ref:
                zip_ref.extractall(target_path)
        except Exception as e:
            logging.error(f"Error while unzipping {source_path}: {e}")
            raise e

    @staticmethod
    def copy(source_path: Path, target_path: str = "./"):
        """copy a folder or file from `source_path` to `target_path`"""

        try:
            if Path(source_path).is_file():
                shutil.copy2(src=source_path, dst=target_path)
            else:
                copy_tree(src=source_path, dst=target_path)
        except Exception as e:
            logging.error(f"Error while copying {source_path} to {target_path}: {e}")
            raise e

    @staticmethod
    def dict_to_lowercase(target_dict: dict, string_conversion: bool = True) -> dict:
        """transform values and keys in dict to lowercase, optionally with string conversion of the values.

        Warning: Does not convert nested dicts in the `target_dict`, but rather removes them from return object.
        """

        if string_conversion:
            # keys should always be strings per default. values might differ in type.
            return dict((k.lower(), str(v).lower()) for k, v in target_dict.items())
        else:
            return dict((k.lower(), v.lower()) for k, v in target_dict.items())

    @staticmethod
    def list_to_lowercase(target_list: list) -> list:
        """string conversion and lower-casing of values in list.

        trade-off: String conversion for increased robustness > type failure detection
        """

        return [str(x).lower() for x in target_list]

    @staticmethod
    def deep_get(base_dict: dict, key: str):
        """Split the key by "." to get value in nested dictionary."""
        try:
            key_split = key.split(".")
            for key_ in key_split:
                base_dict = base_dict[key_]
            return base_dict
        except TypeError as e:
            logging.debug(
                f"No key ({key}) found in base_dict ({base_dict}) for this model. Fallback: Returning None."
            )
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
    def has_more_than_n_diff_pixel_values(img: np.ndarray, n: int =4) -> bool:
        """ This function checks whether an image contains more than n different pixel values.

        This helps to differentiate between segmentation masks and actual images.
        """

        import torch
        torch_img = torch.from_numpy(img)
        pixel_values_set = set(torch_img.flatten().tolist())
        if len(pixel_values_set) > n:
            return True
        else:
            return False

    @staticmethod
    def split_images_and_masks(data: list, num_samples: int, max_nested_arrays: int = 2) -> [np.ndarray, np.ndarray]:
        """ Extracts and separates the masks from the images if a model returns both in the same np.ndarray.

        This extendable function assumes that, in data, a mask follows the image that it corresponds to or vice versa.
        """

        images = []
        masks = []
        # if data is smaller than the number of samples that should have been generated, then data likely contains a nested array.
        # We go a maximum of max_nested_arrays deep into the data.
        counter = 0
        while len(data) < num_samples:
            data = data[0]
            counter = counter + 1
            if counter >= max_nested_arrays:
                break

        for data_point in data:
            if isinstance(data_point, tuple):
                for i in data_point:
                    if isinstance(i, np.ndarray) and "int" in str(i.dtype) and not Utils.has_more_than_n_diff_pixel_values(i):
                        # Check if numpy array that contains integers instead of floats indicates the presence of a mask
                        masks.append(i)
                    elif Utils.has_more_than_n_diff_pixel_values(i):
                        images.append(i)
            elif isinstance(data_point, np.ndarray) and "int" in str(data_point.dtype) and not Utils.has_more_than_n_diff_pixel_values(data_point):
                masks.append(data_point)
            else:
                images.append(data_point)
        masks = None if len(masks)==0 else masks
        return images, masks


    @staticmethod
    def order_dict_by_value(dict_list, key: str, order: str = "asc", sort_algorithm="bubbleSort") -> list:
        """Sorting a list of dicts by the values of a specific key in the dict using a sorting algorithm.

        - This function is deprecated. You may use Python List sort() with key=lambda function instead.

        """

        if sort_algorithm == "bubbleSort":
            for i in range(len(dict_list)):
                for j in range(len(dict_list) - i - 1):
                    if dict_list[j][key] > dict_list[j + 1][key]:
                        # no need for a temp variable holder
                        dict_list[j][key], dict_list[j + 1][key] = (
                            dict_list[j + 1][key],
                            dict_list[j][key],
                        )
        return dict_list


    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
