# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" `Utils` class providing generalized reusable functions for I/O, parsing, sorting, type conversions, etc. """
# Import python native libs
import json
import logging
import os
import shutil
import time
import zipfile
from distutils.dir_util import copy_tree
from pathlib import Path
from urllib.parse import urlparse  # python3

import numpy as np

# Import pypi libs
import requests
from tqdm import tqdm


class Utils:
    """Utils class containing reusable static methods."""

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
    def download_file(
        download_link: str, path_as_string: str, file_extension: str = ".json"
    ):
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
                    total=total_size_in_bytes,
                    unit="B",
                    unit_scale=True,
                    position=0,
                    leave=True,
                    ascii=True,
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
                    if not (
                        download_link.endswith(file_extension)
                        and Path(path_as_string).is_file()
                        and str(path_as_string).endswith(file_extension)
                    ):
                        # If we do not download a json file (global.json), we assume a zip and want to check if the downloaded zip is valid.
                        zipfile.ZipFile(path_as_string, "r")
                    break
                except Exception as e:
                    print(e)
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
    def unzip_and_return_unzipped_path(package_path: str):
        """if not already dir, unzip an archive with `Utils.unzip_archive`. Return path to unzipped dir/file"""

        if Path(package_path).is_file() and package_path.endswith(".zip"):
            # Get the source_path without .zip extension to unzip.
            package_path_unzipped = package_path[0:-4]
            # We have a zip. Let's unzip and do the same operation (with new path)
            Utils.unzip_archive(
                source_path=package_path, target_path_as_string=package_path_unzipped
            )
            return package_path_unzipped
        elif Path(package_path).is_dir():
            logging.info(
                f"Your package path ({package_path}) does already point to a directory. It was not unzipped."
            )
            return package_path
        else:
            raise Exception(
                f"Your package path ({package_path}) does not point to a zip file nor directory. Please adjust and try again."
            )

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
        """Checks if a url is valid using urllib.parse.urlparse"""

        try:
            result = urlparse(the_url)
            # testing if both result.scheme and result.netloc are non-empty strings (empty strings evaluate to False).
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def has_more_than_n_diff_pixel_values(img: np.ndarray, n: int = 4) -> bool:
        """This function checks whether an image contains more than n different pixel values.

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
    def split_images_masks_and_labels(
        data: list, num_samples: int, max_nested_arrays: int = 2
    ) -> [list, list, list, list]:
        """Separates the data (sample, mask, other_imaging_data, label) returned by a generative model

        This functions expects a list of tuples as input `data` and assumes that each
        tuple contains sample, mask, other_imaging_data, label at index positions [0], [1], [2], and [3] respectively.

        samples, masks, and imaging data are expected to be of type np.ndarray and labels of type "str".

        For example, this extendable function assumes that, in data, a mask follows the image that it
        corresponds to or vice versa.
        """

        samples = []
        masks = []
        other_imaging_output = []
        labels = []
        # if data is smaller than the number of samples that should have been generated, then data likely contains a nested array.
        # We go a maximum of max_nested_arrays deep into the data.
        counter = 0
        while len(data) < num_samples and isinstance(data, list):
            data = data[0]
            counter = counter + 1
            if counter >= max_nested_arrays:
                break

        for data_point in data:
            logging.debug(f"data_point: {data_point}")
            if isinstance(data_point, tuple):
                for i, item in enumerate(data_point):
                    if isinstance(item, np.ndarray) and i == 0:
                        samples.append(item)
                    elif isinstance(item, np.ndarray) and i == 1:
                        masks.append(item)
                    elif isinstance(item, np.ndarray) and i == 2:
                        other_imaging_output.append(item)
                    elif isinstance(item, str):
                        labels.append(item)
            elif isinstance(data_point, np.ndarray):
                # An image is expected in the case no tuple is returned
                samples.append(data_point)
        masks = None if len(masks) == 0 else masks
        other_imaging_output = (
            None if len(other_imaging_output) == 0 else other_imaging_output
        )
        labels = None if len(labels) == 0 else labels
        return samples, masks, other_imaging_output, labels

    @staticmethod
    def split_images_and_masks_no_ordering(
        data: list, num_samples: int, max_nested_arrays: int = 2
    ) -> [np.ndarray, np.ndarray]:
        """Extracts and separates the masks from the images if a model returns both in the same np.ndarray.

        This extendable function assumes that, in data, a mask follows the image that it corresponds to or vice versa.

        - This function is deprecated. Please use `split_images_masks_and_labels` instead.
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
            logging.debug(f"data_point {data_point}")
            if isinstance(data_point, tuple):
                for i, sample in enumerate(data_point):
                    if (
                        isinstance(i, np.ndarray)
                        and "int" in str(i.dtype)
                        and not Utils.has_more_than_n_diff_pixel_values(i)
                    ):
                        # Check if numpy array that contains integers instead of floats indicates the presence of a mask
                        masks.append(i)
                    elif Utils.has_more_than_n_diff_pixel_values(i):
                        images.append(i)
            elif (
                isinstance(data_point, np.ndarray)
                and "int" in str(data_point.dtype)
                and not Utils.has_more_than_n_diff_pixel_values(data_point)
            ):
                masks.append(data_point)
            else:
                images.append(data_point)
        masks = None if len(masks) == 0 else masks
        return images, masks

    @staticmethod
    def order_dict_by_value(
        dict_list, key: str, order: str = "asc", sort_algorithm="bubbleSort"
    ) -> list:
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

    @staticmethod
    def is_file_in(folder_path: str, filename: str) -> bool:
        """Checks if a file is inside a folder"""

        try:
            if (
                Path(folder_path).is_dir()
                and Path(f"{folder_path}/{filename}").is_file()
            ):
                return True
        except Exception as e:
            logging.warning(f"File ({filename}) was not found in {folder_path}: {e}")
            return False

    @staticmethod
    def store_dict_as(
        dictionary,
        extension: str = ".json",
        output_path: str = "config/",
        filename: str = "metadata.json",
    ):
        """store a Python dictionary in file system as variable filetype."""

        if extension not in output_path:
            Utils.mkdirs(path_as_string=output_path)
            if extension not in filename:
                filename = filename + extension
            output_path = f"{output_path}/{filename}"
        json_object = json.dumps(dictionary, indent=4)
        with open(output_path, "w") as outfile:
            outfile.write(json_object)

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
