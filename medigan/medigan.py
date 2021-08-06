from pathlib import Path
from typing import Union
import yaml
import numpy as np
import cv2
import os
import requests
from urllib.request import Request, urlopen
import json
import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict
import importlib
import zipfile


        
def get_the_model_url(model_name,url,extension):
    model_path = Path(f"my_models/{model_name}{extension}")
    if not os.path.exists("my_models/"):
        os.makedirs("my_models/")
    try:
        models_abs_path = model_path.resolve(strict=True)
    except FileNotFoundError:
        try:
            print(f"Downloading {model_name}....")
            r = requests.get(url, allow_redirects=True)
            open(f'my_models/{model_name}{extension}', 'wb').write(r.content)
        except:
            print("can't download this model...")
    return model_path


def orch_module_url(file_name,url,extension):
    file_path = Path(f"config/{file_name}{extension}")
    if not os.path.exists("config/"):
        os.makedirs("config/")
    try:
        file_abs_path = file_path.resolve(strict=True)
    except FileNotFoundError:
        try:
            print(f"Downloading {file_name}....")
            r = requests.get(url, allow_redirects=True)
            open(f'config/{file_name}{extension}', 'wb').write(r.content)
        except:
            print("can't download this file...")
    return file_path
                  

def orch_packages(file_name,url):
    file_path = Path(f"packages/{file_name}.zip")
    if not os.path.exists("packages/"):
        os.makedirs("packages/")
    try:
        file_abs_path = file_path.resolve(strict=True)
    except FileNotFoundError:
        try:
            print(f"Downloading packages at {file_name}....")
            r = requests.get(url, allow_redirects=True)
            open(f'packages/{file_name}.zip', 'wb').write(r.content)
        except:
            print("can't download this file...")
            
    return file_path
        
def decompress_files(file_link):
    print(f"decompressing {file_link}....")
    with zipfile.ZipFile(file_link, 'r') as zip_ref:
        zip_ref.extractall("./")
           
        
        
def generate_dataset(model_name,number_samples,output):
    # TODO Move packages to zenodo..
    decompress_files(orch_packages("packages","https://noussair.com/ub/packages.zip"))
    orch_file = orch_module_url("global","https://raw.githubusercontent.com/RichardObi/medigan-models/main/global.json",".json");
    # orch_file = orch_module_url("global","https://zenodo.org/record/5077840/files/orch.json?download=1",".json");
    with open(orch_file) as f:
        models_lists = json.load(f)

    if model_name in models_lists:
        print("model is available")
        module_list = models_lists[model_name]["dependencies"]
        module_link = models_lists[model_name]["model_link"]
        extension = models_lists[model_name]["extension"]
        package_name = models_lists[model_name]["package_name"]
        full_module_name = "packages." + package_name
        
        print (module_link)
        print("checking dependencies availability")
        try:
            pkg_resources.require(module_list)
            print ("all dependencies are available")
        except:
            print("Missing dependencies")
       
        
        model_file = get_the_model_url(model_name,module_link,extension)
        generator_function = models_lists[model_name]["generator"]["name"]
        print(f"generator file : {generator_function}")
        print (f"Importing....{full_module_name}")
        the_module = importlib.import_module(full_module_name)
        print ("Successfully imported ")
        the_module.generate_GAN_images(model_file, 120, number_samples,output)

        
    else:
        print("model not available")
        
def get_meta_data(model_name,dim):
    orch_file = orch_module_url("global","https://zenodo.org/record/5077840/files/orch.json?download=1",".json");
    with open(orch_file) as f:
        models_lists = json.load(f)   
         
    if model_name in models_lists:
        return (models_lists[model_name]["meta"])
        
    else:
        print("model not available")
        


