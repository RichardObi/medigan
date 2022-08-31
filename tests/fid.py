"""
Calculates the Frechet Inception Distance between two distributions, using chosen feature extractor model.

RadImageNet Model source: https://github.com/BMEII-AI/RadImageNet
RadImageNet InceptionV3 weights: https://drive.google.com/file/d/1p0q9AhG3rufIaaUE1jc2okpS8sdwN6PU

Usage:
    python fid.py dir1 dir2 
"""
import argparse
import os

import cv2
import numpy as np
import tensorflow as tf
import tensorflow_gan as tfgan
import wget
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.applications.inception_v3 import preprocess_input

img_size = 299
batch_size = 64
num_batches = 1
RADIMAGENET_URL = "https://drive.google.com/uc?id=1p0q9AhG3rufIaaUE1jc2okpS8sdwN6PU"
RADIMAGENET_WEIGHTS = "RadImageNet-InceptionV3_notop.h5"
IMAGENET_TFHUB_URL = "https://tfhub.dev/tensorflow/tfgan/eval/inception/1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculates the Frechet Inception Distance between two distributions using RadImageNet model."
    )
    parser.add_argument(
        "dataset_path_1",
        type=str,
        help="Path to images from first dataset",
    )
    parser.add_argument(
        "dataset_path_2",
        type=str,
        help="Path to images from second dataset",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="imagenet",
        help="Use RadImageNet feature extractor for FID calculation",
    )
    parser.add_argument(
        "--lower_bound",
        action="store_true",
        help="Calculate lower bound of FID using the 50/50 split of images from dataset_path_1",
    )
    parser.add_argument(
        "--normalize_images",
        action="store_true",
        help="Normalize images from both datasources using min and max of each sample",
    )
    args = parser.parse_args()
    return args


def load_images(directory, normalize=False, split=False, limit=None):
    """
    Loads images from the given directory.
    If split is True, then half of the images is loaded to one array and the other half to another.
    """
    if split:
        subset_1 = []
        subset_2 = []
    else:
        images = []

    for count, filename in enumerate(os.listdir(directory)):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            img = cv2.imread(os.path.join(directory, filename))
            img = cv2.resize(img, (img_size, img_size), interpolation=cv2.INTER_LINEAR)
            if normalize:
                img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
            if len(img.shape) > 2 and img.shape[2] == 4:
                img = img[:, :, :3]
            if len(img.shape) == 2:
                img = np.stack([img] * 3, axis=2)

            if split:
                if count % 2:
                    subset_1.append(img)
                else:
                    subset_2.append(img)
            else:
                images.append(img)
        if count == limit:
            break
    if split:
        subset_1 = preprocess_input(np.array(subset_1))
        subset_2 = preprocess_input(np.array(subset_2))
        return subset_1, subset_2
    else:
        images = preprocess_input(np.array(images))
        return images


def check_model_weights(model_name):
    """
    Checks if the model weights are available and download them if not.
    """
    model_weights_path = None
    if model_name == "radimagenet":
        model_weights_path = RADIMAGENET_WEIGHTS
        if not os.path.exists(RADIMAGENET_WEIGHTS):
            print("Downloading RadImageNet InceptionV3 model:")
            wget.download(
                RADIMAGENET_URL,
                model_weights_path,
            )
            print("\n")
        return model_weights_path


def _radimagenet_fn(images):
    """
    Get RadImageNet inception v3 model
    """
    model = InceptionV3(
        weights=RADIMAGENET_WEIGHTS,
        input_shape=(img_size, img_size, 3),
        include_top=False,
        pooling="avg",
    )
    output = model(images)
    output = tf.nest.map_structure(tf.keras.layers.Flatten(), output)
    return output


def get_classifier_fn(model_name="imagenet"):
    """
    Get model as TF function for optimized inference.
    """
    check_model_weights(model_name)

    if model_name == "radimagenet":
        return _radimagenet_fn
    elif model_name == "imagenet":
        return tfgan.eval.classifier_fn_from_tfhub(IMAGENET_TFHUB_URL, "pool_3", True)
    else:
        raise ValueError("Model {} not recognized".format(model_name))


def calculate_fid(directory_1, directory_2, model_name, normalize_images=False, lower_bound=False):
    """
    Calculates the Frechet Inception Distance between two distributions using chosen feature extractor model.
    """
    limit = min(len(os.listdir(directory_1)), len(os.listdir(directory_2)))
    if lower_bound:
        images_1, images_2 = load_images(directory_1, split=True, limit=limit)
    else:
        images_1 = load_images(directory_1, limit=limit, normalize=normalize_images)
        images_2 = load_images(directory_2, limit=limit, normalize=normalize_images)

    fid = tfgan.eval.frechet_classifier_distance(
        images_1, images_2, get_classifier_fn(model_name)
    )

    return fid


if __name__ == "__main__":
    args = parse_args()

    directory_1 = args.dataset_path_1
    directory_2 = args.dataset_path_2
    lower_bound = args.lower_bound
    normalize_images = args.normalize_images
    model_name = args.model

    fid = calculate_fid(directory_1, directory_2, model_name, lower_bound, normalize_images)

    if lower_bound:
        print("Lower bound FID {}: {}".format(model_name, fid))
    else:
        print("FID {}: {}".format(model_name, fid))
