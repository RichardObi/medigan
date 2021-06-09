from pathlib import Path
from typing import Union
import yaml
import numpy as np
from src.models.predefined.dcgan.generator import Generator
import cv2
import torch
import os


def load_yaml(path: Union[str, Path]):
    with open(path, "r") as yaml_file:
        try:
            return yaml.safe_load(yaml_file)
        except yaml.YAMLError as exc:
            print(exc)
            return {}


def interval_mapping(image, from_min, from_max, to_min, to_max):
    # map values from [from_min, from_max] to [to_min, to_max]
    # image: input array
    from_range = from_max - from_min
    to_range = to_max - to_min
    # scale to interval [0,1]
    scaled = np.array((image - from_min) / float(from_range), dtype=float)
    # multiply by range and add minimum to get interval [min,range+min]
    return to_min + (scaled * to_range)


    
def image_generator(model_path,device,nz,ngf,nc,ngpu,image_size,is_conditional,num_samples):
    # instantiate the model
    print("Instantiating model...")
    netG = Generator(
        nz=nz,
        ngf=ngf,
        nc=nc,
        ngpu=ngpu,
        image_size=image_size,
        is_conditional=is_conditional,
    )

    # load the model's weights from state_dict *'.pt file
    print("Loading model weights...")
    
    checkpoint = torch.load(model_path, map_location=device)
    try:
        netG.load_state_dict(state_dict=checkpoint["generator_state_dict"])
    except KeyError:
        raise KeyError(f"checkpoint['generator_state_dict'] was not found. checkpoint={checkpoint}")
    print(f'Using model retrieved ')
    netG.eval()

    # generate the images
    print("Generating images...")
    z = torch.randn(num_samples, nz, 1, 1, device=device)
    images = netG(z).detach().cpu().numpy()
    image_list = []
    for j, img_ in enumerate(images):
        image_list.append(img_)
        
    return image_list

def show_images(image_list):
    for img_ in image_list:
        img_ = interval_mapping(img_.transpose(1, 2, 0), -1.0, 1.0, 0, 255)
        img_ = img_.astype("uint8")
        cv2.imshow("sample", img_ * 2)
        k = cv2.waitKey()
        if k == 27 or k == 32:  # Esc key or space to stop
            break
    cv2.destroyAllWindows()
    
    
def save_generated_images(image_list, path):
    print("Saving generated images now")

    for i, img_ in enumerate(image_list):
        Path(path).mkdir(parents=True, exist_ok=True)
        img_path = f"{path}/image_DCGAN_{i}.png"
        
        img_ = interval_mapping(img_.transpose(1, 2, 0), -1.0, 1.0, 0, 255)
        img_ = img_.astype("uint8")
        cv2.imwrite(img_path, img_)
    print(f"Saved generated images to {path}")
    
    
def generate_GAN_images(gan_type, device, image_size,num_samples,output_path):
    models_lists = {"DCGAN": "dcgan/model.pt", 
                    "CYCLEGAN": "cyclegan/model.pt",
                   }
    if gan_type in models_lists:
        image_list = image_generator(f"./src/models/predefined/dcgan/model.pt",device,100,64,1,1,128,0, num_samples)
        save_generated_images(image_list, output_path)
    else:
        print("we can't find this type of GAN")

        
        
    
    