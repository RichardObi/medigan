# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" Functionality for automated installation of a model's python package dependencies. """

import argparse
import subprocess
import sys

try:
    # if called as script (__main__) or from inside medigan
    from ..config_manager import ConfigManager
    from ..constants import CONFIG_FILE_KEY_DEPENDENCIES, CONFIG_FILE_KEY_EXECUTION
except:
    # if called from outside medigan
    from medigan.config_manager import ConfigManager
    from medigan.constants import (
        CONFIG_FILE_KEY_DEPENDENCIES,
        CONFIG_FILE_KEY_EXECUTION,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_id",
        type=str,
        default=None,
        nargs="+",
        help="Model ids to install dependencies for",
    )
    args = parser.parse_args()
    return args


def install_model(
    model_id: str, config_manager: ConfigManager = None, execution_config: dict = None
):
    """installing the dependencies required for this model as stated in config"""

    if execution_config is None:
        if config_manager is None:
            config_manager = ConfigManager()
        config = config_manager.get_config_by_id(model_id)
        execution_config = config[CONFIG_FILE_KEY_EXECUTION]
    dependencies = execution_config[CONFIG_FILE_KEY_DEPENDENCIES]
    for package in dependencies:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


if __name__ == "__main__":
    """
    This script is used to install dependencies for models.
    If no model_id is provided, all models from the config file are installed.
    """
    args = parse_args()

    config_manager = ConfigManager()

    if args.model_id:
        for model_id in args.model_id:
            install_model(model_id)
    else:
        for model_id in config_manager.config_dict.keys():
            install_model(model_id)
