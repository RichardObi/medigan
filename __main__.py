import argparse
from pathlib import Path
from time import time
import cv2
import torch
import os

from src.models.predefined.dcgan.generator import Generator
from src.utils.utils import load_yaml
from src.utils.utils import interval_mapping


def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model_checkpoint_path",
        type=str,
        default=None,
        help="Path to model checkpoint .pt file",
    )
    parser.add_argument(
        "--num_samples",
        type=int,
        default=10,
        help="How many samples to generate",
    )
    parser.add_argument(
        "--dont_show_images",
        action="store_true",
        help="Whether to show the generated images in UI.",
    )
    parser.add_argument(
        "--save_images",
        action="store_true",
        help="Whether to save the generated images.",
    )
    parser.add_argument(
        "--out_images_path",
        type=str,
        default=None,
        help="Directory to save the generated images in.",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    # Save the images to model checkpoint folder
    if args.model_checkpoint_path is None:
        args.model_checkpoint_path = Path("src/models/predefined/dcgan/")

    # Get the correct torch device to run model on
    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    # Load model config
    print("Loading config...")
    try:
        yaml_path = next(Path(args.model_checkpoint_path).rglob("*.yaml"))
    except(StopIteration):
        raise (f'No *.yaml file in yaml_path: {args.model_checkpoint_path}')
    config_dict = load_yaml(path=yaml_path)
    print(f'Using config retrieved from: {args.model_checkpoint_path}')

    # instantiate the model
    print("Instantiating model...")
    netG = Generator(
        nz=config_dict.get("nz"),
        ngf=config_dict.get("ngf"),
        nc=config_dict.get("nc"),
        ngpu=config_dict.get("ngpu"),
        image_size=config_dict.get("image_size"),
        is_conditional=config_dict.get("is_conditional"),
    )

    # load the model's weights from state_dict *'.pt file
    print("Loading model weights...")
    try:
        model_path = next(Path(args.model_checkpoint_path).rglob("*.pt"))
    except(StopIteration):
        raise (f'No *.pt file in model_path: {args.model_checkpoint_path}')
    checkpoint = torch.load(model_path, map_location=device)
    try:
        netG.load_state_dict(state_dict=checkpoint["generator_state_dict"])
    except KeyError:
        raise KeyError(f"checkpoint['generator_state_dict'] was not found. checkpoint={checkpoint}")
    print(f'Using model retrieved from: {args.model_checkpoint_path}')
    netG.eval()

    # generate the images
    print("Generating images...")
    z = torch.randn(args.num_samples, config_dict.get("nz"), 1, 1, device=device)
    images = netG(z).detach().cpu().numpy()
    image_list = []
    for j, img_ in enumerate(images):
        image_list.append(img_)

    # Show the images in interactive UI
    if args.dont_show_images is False:
        print("Showing generated images...")
        for img_ in image_list:
            img_ = interval_mapping(img_.transpose(1, 2, 0), -1.0, 1.0, 0, 255)
            img_ = img_.astype("uint8")
            cv2.imshow("sample", img_ * 2)
            k = cv2.waitKey()
            if k == 27 or k == 32:  # Esc key or space to stop
                break
        cv2.destroyAllWindows()

    # Save the images to model checkpoint folder
    if args.out_images_path is None and args.save_images:
        args.out_images_path = Path(f"generated_with_{config_dict.get('model_name')}_at_{time()}")

    if args.out_images_path is not None and not args.out_images_path.exists() and args.save_images:
        os.makedirs(args.out_images_path.resolve())

    if args.save_images:
        print("Saving generated images...")
        for i, img_ in enumerate(image_list):
            img_path = args.out_images_path / f"{config_dict.get('model_name')}_{i}_{time()}.png"
            img_ = interval_mapping(img_.transpose(1, 2, 0), -1.0, 1.0, 0, 255)
            img_ = img_.astype("uint8")
            cv2.imwrite(str(img_path.resolve()), img_)
        print(f"Saved generated images to {args.out_images_path.resolve()}")
