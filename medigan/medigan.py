from pathlib import Path
from typing import Union
import yaml
import numpy as np
from src.models.predefined.dcgan.generator import Generator
import cv2
import torch
import os
import requests
from urllib.request import Request, urlopen


def get_model_url(model_name,url):
    if not os.path.exists("my_models/"):
        os.makedirs("my_models/")
    try:
        print("Downloading....")
        r = requests.get(url, allow_redirects=True)
        open('my_models/'+model_name+".css", 'wb').write(r.content)
    except:
        print("can't download this model...")



def load_yaml(path):
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
    model_file=get_model_url(gan_type)
    if model_file:
        image_list = image_generator(model_file,device,100,64,1,1,128,0, num_samples)
        save_generated_images(image_list, output_path)
    else:
        print("we can't find this type of GAN")

def get_model_url(model_name):
    models_lists = {"DCGAN": "https://zenodo.org/record/4914384/files/DCGAN.pt?download=1", 
                    "CYCLEGAN": "cyclegan/model.pt",
                   }
    model_path = Path(f"my_models/{model_name}.pt")
    if model_name in models_lists:
        print(models_lists[model_name])
        if not os.path.exists("my_models/"):
            os.makedirs("my_models/")
        try:
            models_abs_path = model_path.resolve(strict=True)
        except FileNotFoundError:
            try:
                print(f"Downloading {model_name}....")
                r = requests.get(models_lists[model_name], allow_redirects=True)
                open(f'my_models/{model_name}.pt', 'wb').write(r.content)
            except:
                print("can't download this model...")
        return model_path
    else:
        print(f"{model_name} Does not exist!")
                  
            
    
        
   
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)
#generate_GAN_images("DCGAN", device, 120, 20,"generated_with_DCGAN")

#get_model_url("DCGAN")