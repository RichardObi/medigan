import logging
import os
from pathlib import Path

from PIL import Image

from .geometry import get_random_image


def normalise(data, nmax=1.0, nmin=0.0):
    """Image normalization of pixel values"""

    return (data - data.min()) * (
        (nmax - nmin) / (data.max() - data.min() + 1e-8)
    ) + nmin


def save_generated_masks(images_to_save, output_dir):
    """Saving of the generated masks in output_dir"""

    logging.debug(f"output_filepath: {output_dir}")
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        for i, mask in enumerate(images_to_save):
            mask = normalise(mask, 255, 0)
            mask_pil = Image.fromarray(mask).convert("L")
            mask_pil.save(os.path.join(output_dir, f"{i}.png"))
        logging.debug(f"Saved all masks to {output_dir}")
    except Exception as e:
        logging.error(
            f"Error while trying to save generated masks in {output_dir}: {e}"
        )
        raise e


def generate(model_file, image_size, num_samples, save_images, output_path, shapes):
    """Generating and returning the bezier curve based masks"""
    if image_size < 256:
        logging.warning(
            f"You provided an image size of {image_size}. "
            f"This will affect the output masks as the bezier curve model is optimized to "
            f"create masks for an image size of 256. Please revise."
        )
    try:
        logging.debug("Generating masks...")

        # Using default image size
        if isinstance(image_size, int):
            patch_size = (image_size, image_size)

        elif isinstance(image_size, list) and len(image_size) == 2:
            patch_size = (image_size[0], image_size[1])
        else:
            raise Exception(
                f"image_size needs to be either of type int or of type list with len==2. You provided {image_size}."
            )

        masks = get_synthetic_masks(
            num_samples=num_samples,
            shapes=shapes,
            patch_size=patch_size,
        )
        if save_images:
            save_generated_masks(masks, output_path)
        else:
            return masks
    except Exception as e:
        logging.error(f"Error while trying to generate {num_samples} masks: {e}")
        raise e


def get_synthetic_masks(
    num_samples,
    shapes=["oval", "lobulated", "nodular", "stellate", "irregular"],
    patch_size=(256, 256),
):
    """Generate n masks of tumour masses of given shape type of variable height and width.

    Attributes
    ----------
    num_samples : int
        how many synthetic images to generate.
    shapes : list - default ['oval', 'lobulated', 'nodular', 'stellate', 'irregular']
        complexity of random masks. Only two options are available for now.
    patch_size : tuple - default (32, 32)
        not to be mistaken by the input and output sizes of the mask inside the patch.
        min (16, 16); max (64, 64)

    Returns
    -------
    list
        each element is a mask.
    """

    x, y = patch_size
    masks = []
    for i in range(num_samples):
        mask = get_random_image(x, y, shapes)
        masks.append(mask)
    logging.debug(f" len(masks) {len(masks)}, shape: {masks[0].shape} ")
    return masks
