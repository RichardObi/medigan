<!-- # MEDIGAN -->
<!-- ![medigan](medigan_logo_1.png) -->
![medigan](docs/source/_static/medigan_logo.png)

![Continuous integration](https://github.com/RichardObi/medigan/actions/workflows/python-ci.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/medigan.svg)](https://badge.fury.io/py/medigan)
[![Downloads](https://img.shields.io/pypi/dm/medigan)](https://img.shields.io/pypi/dm/medigan)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6327625.svg)](https://doi.org/10.5281/zenodo.6327625)


#### MEDIGAN - A Modular Python Library For Automating Synthetic Dataset Generation.

While being extendable to any modality and generative model, medigan focuses on automating medical image dataset synthesis using GANs for training deep learning models.

## Features:

- Researchers and ML-practitioners can conveniently use an existing model in `medigan` for synthetic data augmentation instead of having to train their own generative model each time.

- Search and find a model using search terms (e.g. "Mammography, 128x128, DCGAN") or key value pairs (e.g. `key` = "modality", `value` = "Mammography")

- Explore the config and information (metrics, use-cases, modalities, etc) of each model in `medigan`

- Generate samples using a model

- Get the generate_method of a model to use dynamically inside your app

## Available models

| Type                        | Modality |     Model     |   Size   | Base dataset | Sample  |  ID   |
|-----------------------------|:--------:|:-------------:|:--------:|:------------:|:------:|:------:|
| Breast Calcification        |   x-ray  |     dcgan     |  128x128 |   Inbreast   |  ![sample](docs/source/_static/samples/00001.png) | <sub> 00001_DCGAN_MMG_CALC_ROI </sub>  | 
| Breast Mass                 |   x-ray  |     dcgan     |  128x128 |    Optimam   |  ![sample](docs/source/_static/samples/00002.png) | <sub> 00002_DCGAN_MMG_MASS_ROI </sub>         |
| Breast Density Transfer     |   x-ray  |    cyclegan   | 1332x800 |     BCDR     |  ![sample](docs/source/_static/samples/00003.png) | <sub> 00003_CYCLEGAN_MMG_DENSITY_FULL </sub>  |
| Breast Mask to Mass         |   x-ray  |    pix2pix    |  256x256 |     BCDR     |  ![sample](docs/source/_static/samples/00004.png) | <sub> 00004_PIX2PIX_MASKTOMASS_BREAST_MG_SYNTHESIS </sub> |
| Breast Mass                 |   x-ray  |     dcgan     |  128x128 |     BCDR     |  ![sample](docs/source/_static/samples/00005.png) | <sub> 00005_DCGAN_MMG_MASS_ROI </sub>         | 
| Breast Mass                 |   x-ray  |    wgan-gp    |  128x128 |     BCDR     |  ![sample](docs/source/_static/samples/00006.png) | <sub> 00006_WGANGP_MMG_MASS_ROI </sub>        | 

[comment]: <> (| Spine Bone Cement Injection |    CT    |    biceps     |  128x128 |     VerSe    | <sub> to be announced </sub>                  |        |)

The metadata and links to the models in medigan are stored in: https://github.com/RichardObi/medigan-models

## Installation
To install the current release, simply run:
```python
pip install medigan
```

## Getting Started
Examples and notebooks are located at [examples](examples) folder

Documentation is available at [medigan.readthedocs.io](https://medigan.readthedocs.io/en/latest/)


### Generation example
#### DCGAN 
Create mammography calcification images using DCGAN model
```python
# import medigan and initialize Generators
from medigan import Generators
generators = Generators()

# generate 6 samples using one of the medigan models
generators.generate(model_id="00001_DCGAN_MMG_CALC_ROI", num_samples=6)
```
![sample](docs/source/_static/samples/dcgan/gan_sample_1.png)
![sample](docs/source/_static/samples/dcgan/gan_sample_2.png)
![sample](docs/source/_static/samples/dcgan/gan_sample_3.png)
![sample](docs/source/_static/samples/dcgan/gan_sample_4.png)
![sample](docs/source/_static/samples/dcgan/3.png)
![sample](docs/source/_static/samples/dcgan/gan_sample_5.png)


#### CYCLEGAN 
Create mammograms translated from Low-to-High Breast Density using CYCLEGAN model
```python
from medigan import Generators
generators = Generators()

generators.generate(model_id="00003_CYCLEGAN_MMG_DENSITY_FULL", num_samples=1)
```
![sample](docs/source/_static/samples/cyclegan/sample_image_5_low.png)
&rarr;
![sample](docs/source/_static/samples/cyclegan/sample_image_5_high.png)


### Search Example
Search for a model inside medigan using keywords
```python
# import medigan and initialize Generators
from medigan import Generators
generators = Generators()

# list all models
print(generators.list_models())

# search for models that have specific keywords in their config
keywords = ['DCGAN', 'Mammography', 'BCDR']
results = generators.find_matching_models_by_values(keywords)
```

### Get Model as Dataloader 
We can directly receive a [torch.utils.data.DataLoader](https://pytorch.org/docs/stable/data.html#torch.utils.data.DataLoader) object for any of medigan's generative models.
```python
from medigan import Generators
generators = Generators()
dataloader = generators.get_as_torch_dataloader(model_id="00004_PIX2PIX_MASKTOMASS_BREAST_MG_SYNTHESIS", num_samples=3)
```

Visualize the contents of the dataloader.
```python
from matplotlib import pyplot as plt
import numpy as np

plt.figure()
# subplot with 2 rows and len(dataloader) columns
f, img_array = plt.subplots(2, len(dataloader)) 

for batch_idx, data_dict in enumerate(dataloader):
    sample = np.squeeze(data_dict.get("sample"))
    mask = np.squeeze(data_dict.get("mask"))
    img_array[0][batch_idx].imshow(sample, interpolation='nearest', cmap='gray')
    img_array[1][batch_idx].imshow(mask, interpolation='nearest', cmap='gray')
plt.show()
```
![sample](docs/source/_static/samples/gan_sample_00004_dataloader.png)

## Contribute A Model

Create an [__init__.py](templates/examples/__init__.py) file in your model's root folder. 

Next, run the following code to push your model to Zenodo.

```python
from medigan import Generators
generators = Generators()

# The model contributor handles 
generators.add_model_contributor(
        model_id="00010_YOUR_MODEL", 
        init_py_path="path/ending/with/__init__.py")

# Input some metadata information for your model.
generators.add_metadata_from_input(
        model_id="00010_YOUR_MODEL", 
        model_weights_name = "10000",
        model_weights_extension=".pt", 
        generate_method_name = "generate", 
        dependencies=["numpy", "torch"])

# Get Zenodo access token: https://zenodo.org/account/settings/applications/tokens/new/
generators.push_to_zenodo(
        model_id="00010_YOUR_MODEL",
        access_token="ACCESS_TOKEN",
        creator_name="NAME",
        creator_affiliation="AFFILIATION")
```

## Contributions in General
We welcome contributions to medigan. Please send us an email or read the [contributing guidelines](CONTRIBUTING.md) on how to contribute to the medigan project.