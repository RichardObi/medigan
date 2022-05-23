import argparse
import subprocess
import sys

from .config_manager import ConfigManager
from .constants import CONFIG_FILE_KEY_DEPENDENCIES, CONFIG_FILE_KEY_EXECUTION


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


def install_model(model_id):

    config = config_manager.get_config_by_id(model_id)
    dependencies = config[CONFIG_FILE_KEY_EXECUTION][CONFIG_FILE_KEY_DEPENDENCIES]
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
