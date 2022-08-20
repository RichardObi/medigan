<!-- # MEDIGAN -->
<!-- ![medigan](medigan_logo_1.png) -->
![medigan](docs/source/_static/medigan_logo.png)

![Continuous integration](https://github.com/RichardObi/medigan/actions/workflows/python-ci.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/medigan.svg)](https://badge.fury.io/py/medigan)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6327625.svg)](https://doi.org/10.5281/zenodo.6327625)

## A modular package for automated synthetic data generation.

- :x: **Problem 1:** Data scarcity in medical imaging. 

- :x: **Problem 2:** Scarcity of readily reusable generative models in medical imaging.

- :white_check_mark: **Solution:** `medigan`
    1. dataset sharing via generative models :gift:
    2. data augmentation :gift:
    3. domain adaptation :gift:
    4. synthetic multi-model datasets for generative model evaluation method testing :gift:

`medigan` provides functions for sharing and re-use of pretrained generative models in medical imaging.

## Features:

- Instead of training your own, use one a generative models from `medigan` to generate synthetic data.

- Search and find a model in `medigan` using search terms (e.g. "Mammography" or "Endoscopy").

- Contribute your own generative model to `medigan` to increase its visibility, re-use, and impact.

## Available models

| Output                       | Modality |     Model     |   Size   | Base dataset | Sample  |  ID   |   Hosted on  |   Reference  |
|-----------------------------|:--------:|:-------------:|:--------:|:------------:|:------:|:------:|:------:|:------:|
| Breast Calcification        |   x-ray  |     dcgan     |  128x128 |   Inbreast   |  ![sample](docs/source/_static/samples/00001.png) | <sub> 00001_DCGAN_MMG_CALC_ROI </sub>  | [Zenodo (5187714)](https://doi.org/10.5281/zenodo.5187714) | | 
| Breast Mass                 |   x-ray  |     dcgan     |  128x128 |    Optimam   |  ![sample](docs/source/_static/samples/00002.png) | <sub> 00002_DCGAN_MMG_MASS_ROI </sub>         | [Zenodo (5188557)](https://doi.org/10.5281/zenodo.5188557) | [Alyafi et al (2019)](https://doi.org/10.48550/arXiv.1909.02062) | 
| Breast Density Transfer     |   x-ray  |    cyclegan   | 1332x800 |     BCDR     |  ![sample](docs/source/_static/samples/00003.png) | <sub> 00003_CYCLEGAN_MMG_DENSITY_FULL </sub>  | [Zenodo (5547263)](https://doi.org/10.5281/zenodo.5547263) | | 
| Breast Mass with Mask       |   x-ray  |    pix2pix    |  256x256 |     BCDR     |  ![sample](docs/source/_static/samples/00004.png) ![sample](docs/source/_static/samples/00004_mask.png) | <sub> 00004_PIX2PIX_MASKTOMASS_BREAST_MG_SYNTHESIS </sub> | [Zenodo (5554950)](https://doi.org/10.5281/zenodo.5554950) |  | 
| Breast Mass                 |   x-ray  |     dcgan     |  128x128 |     BCDR     |  ![sample](docs/source/_static/samples/00005.png) | <sub> 00005_DCGAN_MMG_MASS_ROI </sub>         | [Zenodo (6555188)](https://doi.org/10.5281/zenodo.6555188) | [Szafranowska et al (2022)](https://doi.org/10.48550/arXiv.2203.04961) | 
| Breast Mass                 |   x-ray  |    wgan-gp    |  128x128 |     BCDR     |  ![sample](docs/source/_static/samples/00006.png) | <sub> 00006_WGANGP_MMG_MASS_ROI </sub>        | [Zenodo (6554713)](10.5281/zenodo.6554713) | [Szafranowska et al (2022)](https://doi.org/10.48550/arXiv.2203.04961) | 
| Tumor Mask                  |   x-ray  |    bezier curves    |  256x256 |     BCDR     |  ![sample](docs/source/_static/samples/00007.png) | <sub> 00007_BEZIERCURVE_TUMOUR_MASK </sub>       |  [Github (medigan)](https://github.com/RichardObi/medigan/tree/main/models/00007_BEZIERCURVE_TUMOUR_MASK) | | 
| Breast Mass (Mal/Benign)    |   x-ray  |    c-dcgan     |  128x128 |     CBIS-DDSM     |  ![sample](docs/source/_static/samples/00008.png) | <sub> 00008_C-DCGAN_MMG_MASSES </sub>        | [Zenodo (6647349)](https://doi.org/10.5281/zenodo.6647349) | | 
| Polyp with Mask             |   endoscopy  |    pggan   |  256x256 |     HyperKvasir     |  ![sample](docs/source/_static/samples/00009.png)![sample](docs/source/_static/samples/00009_mask.png) | <sub> 00009_PGGAN_POLYP_PATCHES_W_MASKS </sub>        | [Zenodo (6653743)](https://doi.org/10.5281/zenodo.6653743) | [Thambawita et al (2022)](https://doi.org/10.1371/journal.pone.0267976) | 
| Polyp with Mask             |   endoscopy  |    fastgan |  256x256 |     HyperKvasir     |  ![sample](docs/source/_static/samples/00010.png)![sample](docs/source/_static/samples/00010_mask.png) | <sub> 00010_FASTGAN_POLYP_PATCHES_W_MASKS </sub>      | [Zenodo (6660711)](https://doi.org/10.5281/zenodo.6660711) | [Thambawita et al (2022)](https://doi.org/10.1371/journal.pone.0267976) | 
| Polyp with Mask             |   endoscopy  |    singan |  250x??? |     HyperKvasir     |  ![sample](docs/source/_static/samples/00011.png)![sample](docs/source/_static/samples/00011_mask.png) | <sub> 00011_SINGAN_POLYP_PATCHES_W_MASKS </sub>      | [Zenodo (6667944)](https://doi.org/10.5281/zenodo.6667944) | [Thambawita et al (2022)](https://doi.org/10.1371/journal.pone.0267976) | 
| Breast Mass (Mal/Benign)    |   x-ray  |    c-dcgan     |  128x128 |     BCDR     |  ![sample](docs/source/_static/samples/00012.png) | <sub> 00012_C-DCGAN_MMG_MASSES </sub>        | [Zenodo (6755693)](https://doi.org/10.5281/zenodo.6818095) | | 
| Breast Density Transfer MLO |   x-ray  |    cyclegan   | 1332x800 |     OPTIMAM     |  ![sample](docs/source/_static/samples/00013.png) | <sub> 00013_CYCLEGAN_MMG_DENSITY_OPTIMAM_MLO </sub>  | [Zenodo (6818095)](https://doi.org/10.5281/zenodo.6818095) | | 
| Breast Density Transfer CC  |   x-ray  |    cyclegan   | 1332x800 |     OPTIMAM     |  ![sample](docs/source/_static/samples/00014.png) | <sub> 00014_CYCLEGAN_MMG_DENSITY_OPTIMAM_CC </sub>  | [Zenodo (6818103)](https://doi.org/10.5281/zenodo.6818103) | | 
| Breast Density Transfer MLO |   x-ray  |    cyclegan   | 1332x800 |     CSAW     |  ![sample](docs/source/_static/samples/00015.png) | <sub> 00015_CYCLEGAN_MMG_DENSITY_CSAW_MLO </sub>  | [Zenodo (6818105)](https://doi.org/10.5281/zenodo.6818105) | | 
| Breast Density Transfer CC  |   x-ray  |    cyclegan   | 1332x800 |     CSAW     |  ![sample](docs/source/_static/samples/00016.png) | <sub> 00016_CYCLEGAN_MMG_DENSITY_CSAW_CC </sub>  | [Zenodo (6818107)](https://doi.org/10.5281/zenodo.6818107) | | 
| Lung Nodules                |   x-ray  |    dcgan      | 128x128  |     NODE21     |  ![sample](docs/source/_static/samples/00017.png) | <sub> 00017_DCGAN_XRAY_LUNG_NODULES </sub>  | [Zenodo (6943691)](https://doi.org/10.5281/zenodo.6943691) | | 
| Lung Nodules                |   x-ray  |    wgan-gp      | 128x128  |     NODE21     |  ![sample](docs/source/_static/samples/00018.png) | <sub> 00018_WGANGP_XRAY_LUNG_NODULES </sub>  | [Zenodo (6943761)](https://doi.org/10.5281/zenodo.6943761) | | 
| Chest Xray Images           |   x-ray  |    pggan      | 1024x1024  |     NODE21     |  ![sample](docs/source/_static/samples/00019.png) | <sub> 00019_PGGAN_CHEST_XRAY </sub>  | [Zenodo (6943803)](https://doi.org/10.5281/zenodo.6943803) | | 

[comment]: <> (| Spine Bone Cement Injection |    CT    |    biceps     |  128x128 |     VerSe    | <sub> to be announced </sub>                  |        |)

Model information can be found in the [global.json](https://github.com/RichardObi/medigan/blob/main/config/global.json) model metadata file.

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

## Visualize A Model 
With our interface, it is possible to generate sample by manually setting the conditional inputs or latent vector values. The sample is updated in realtime, so it's possible to observe how the images changes when the parameters are modified. The visualization is available only for models with accessible input latent vector. Depending on a model, a conditional input may be also available or synthetic segmentation mask.
```
from medigan import Generators

generators = Generators()
generators.visualize("00010_FASTGAN_POLYP_PATCHES_W_MASKS")
```

![sample](docs/source/_static/interface.png)

## Contribute A Model

Create an [__init__.py](templates/examples/__init__.py) file in your model's root folder. 

Next, run the following code to contribute your model to medigan.

- Your model will be stored on [Zenodo](https://zenodo.org/). 

- Also, a Github [issue](https://github.com/RichardObi/medigan/issues) will be created to add your model's metadata to medigan's [global.json](https://github.com/RichardObi/medigan/blob/main/config/global.json).

- To do so, please provide a github access token ([get one here](https://github.com/settings/tokens)) and a zenodo access token ([get one here](https://zenodo.org/account/settings/applications/tokens/new/)), as shown below. After creation, the zenodo access token may take a few minutes before being recognized in zenodo API calls.

```python
from medigan import Generators
generators = Generators()

# Contribute your model
generators.contribute(
    model_id = "00100_YOUR_MODEL", # assign an ID
    init_py_path ="path/ending/with/__init__.py",
    model_weights_name = "10000",
    model_weights_extension = ".pt",
    generate_method_name = "generate", # in __init__.py
    dependencies = ["numpy", "torch"], 
    creator_name = "YOUR_NAME",
    creator_affiliation = "YOUR_AFFILIATION",
    zenodo_access_token = 'ZENODO_ACCESS_TOKEN',
    github_access_token = 'GITHUB_ACCESS_TOKEN',
```
Thank you for your contribution! 

You will soon receive a reply in the Github [issue](https://github.com/RichardObi/medigan/issues) that you created for your model by running ```generators.contribute()```.

## Contributions in General
We welcome contributions to medigan. Please send us an email or read the [contributing guidelines](CONTRIBUTING.md) regarding contributing to the medigan project.