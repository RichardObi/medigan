<!-- # MEDIGAN -->
<!-- ![medigan](medigan_logo_1.png) -->
![medigan](docs/source/_static/medigan_logo.png)

[![License](https://img.shields.io/github/license/RichardObi/medigan)](https://opensource.org/licenses/MIT)
![Continuous integration](https://github.com/RichardObi/medigan/actions/workflows/python-ci.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/medigan.svg)](https://badge.fury.io/py/medigan)
[![Conda version](https://img.shields.io/conda/vn/conda-forge/medigan)](https://github.com/conda-forge/medigan-feedstock)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6327625.svg)](https://doi.org/10.5281/zenodo.6327625)
[![arXiv](https://img.shields.io/badge/arXiv-2209.14472-b31b1b.svg)](https://arxiv.org/abs/2209.14472)

`medigan` stands for **medi**cal **g**enerative (**a**dversarial) **n**etworks. `medigan` provides user-friendly medical image synthesis and allows users to choose from a range of pretrained generative models to `generate` synthetic datasets. These synthetic datasets can be used to train or adapt AI models that perform clinical tasks such as lesion classification, segmentation or detection. 

See below how medigan can be run from the command line to generate synthetic medical images.

![medigan can be run directly from the command line to generate synthetic medical images](https://github.com/RichardObi/medigan/blob/main/docs/source/_static/medigan.gif "medigan can be run directly from the command line to generate synthetic medical images.")

## Features:

- :x: **Problem 1:** Data scarcity in medical imaging. 

- :x: **Problem 2:** Scarcity of readily reusable generative models in medical imaging.

- :white_check_mark: **Solution:** `medigan`
    1. dataset sharing via generative models :gift:
    2. data augmentation :gift:
    3. domain adaptation :gift:
    4. synthetic data evaluation method testing with multi-model datasets :gift:

Instead of training your own, use one of the generative models from `medigan` to generate synthetic data. 

Search and find a model in `medigan` using search terms (e.g. "Mammography" or "Endoscopy"). 

Contribute your own generative model to `medigan` to increase its visibility, re-use, and impact.


## Available models

| Output type                                                 |           Modality            |          Model type           |       Output size       |                                                        Base dataset                                                        |                                                                                                                                                                      Output examples                                                                                                                                                                       |                                                                   `model_id`                                                                   |                                    Hosted on                                    |                                      Reference                                       |
|-------------------------------------------------------------|:-----------------------------:|:-----------------------------:|:-----------------------:|:--------------------------------------------------------------------------------------------------------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------:|:------------------------------------------------------------------------------------:|
| <sub> Breast Calcification        </sub>                    |  <sub>  mammography  </sub>   |   <sub>    dcgan     </sub>   |  <sub> 128x128 </sub>   |            <sub>  [Inbreast](https://www.academicradiology.org/article/S1076-6332(11)00451-X/fulltext)   </sub>            |                                                                                                                                                      ![sample](docs/source/_static/samples/00001.png)                                                                                                                                                      |               <sub> [`00001_DCGAN_MMG_CALC_ROI`](https://medigan.readthedocs.io/en/latest/models.html#dcgan-mmg-calc-roi) </sub>               |     <sub>[Zenodo (5187714)](https://doi.org/10.5281/zenodo.5187714) </sub>      |                                                                                      | 
| <sub> Breast Mass                 </sub>                    |  <sub>  mammography  </sub>   |   <sub>    dcgan     </sub>   |  <sub> 128x128 </sub>   |                           <sub>   [Optimam](https://doi.org/10.48550/arXiv.2004.04742)   </sub>                            |                                                                                                                                                      ![sample](docs/source/_static/samples/00002.png)                                                                                                                                                      |               <sub> [`00002_DCGAN_MMG_MASS_ROI`](https://medigan.readthedocs.io/en/latest/models.html#dcgan-mmg-mass-roi) </sub>               |     <sub>[Zenodo (5188557)](https://doi.org/10.5281/zenodo.5188557) </sub>      |     <sub>[Alyafi et al (2019)](https://doi.org/10.48550/arXiv.1909.02062) </sub>     | 
| <sub> Breast Density Transfer     </sub>                    |  <sub>  mammography  </sub>   |   <sub>   cyclegan   </sub>   |  <sub>1332x800 </sub>   |                               <sub>    [BCDR](https://bcdr.eu/information/about)     </sub>                                |                                                                                                                                                      ![sample](docs/source/_static/samples/00003.png)                                                                                                                                                      |        <sub> [`00003_CYCLEGAN_MMG_DENSITY_FULL`](https://medigan.readthedocs.io/en/latest/models.html#cyclegan-mmg-density-full) </sub>        |     <sub>[Zenodo (5547263)](https://doi.org/10.5281/zenodo.5547263) </sub>      |   <sub> [Garrucho et al (2022)](https://doi.org/10.48550/arXiv.2209.09809) </sub>    | 
| <sub> Breast Mass with Mask       </sub>                    |  <sub>  mammography  </sub>   |   <sub>   pix2pix    </sub>   |  <sub> 256x256 </sub>   |                               <sub>    [BCDR](https://bcdr.eu/information/about)     </sub>                                |                                                                                                                        ![sample](docs/source/_static/samples/00004.png) <br> ![sample](docs/source/_static/samples/00004_mask.png)                                                                                                                         | <sub><sub> [`00004_PIX2PIX_MMG_MASSES_W_MASKS`](https://medigan.readthedocs.io/en/latest/models.html#pix2pix-mmg-masses-w-masks) </sub></sub>  |     <sub>[Zenodo (7093759)](https://doi.org/10.5281/zenodo.7093759) </sub>      |                                                                                      | 
| <sub> Breast Mass                 </sub>                    |  <sub>  mammography  </sub>   |   <sub>    dcgan     </sub>   |  <sub> 128x128 </sub>   |                               <sub>    [BCDR](https://bcdr.eu/information/about)     </sub>                                |                                                                                                                                                      ![sample](docs/source/_static/samples/00005.png)                                                                                                                                                      |                      <sub> [`00005_DCGAN_MMG_MASS_ROI`](https://medigan.readthedocs.io/en/latest/models.html#id1) </sub>                       |     <sub>[Zenodo (6555188)](https://doi.org/10.5281/zenodo.6555188) </sub>      |  <sub>[Szafranowska et al (2022)](https://doi.org/10.48550/arXiv.2203.04961) </sub>  | 
| <sub> Breast Mass                 </sub>                    |  <sub>  mammography  </sub>   |   <sub>   wgan-gp    </sub>   |  <sub> 128x128 </sub>   |                               <sub>    [BCDR](https://bcdr.eu/information/about)     </sub>                                |                                                                                                                                                      ![sample](docs/source/_static/samples/00006.png)                                                                                                                                                      |              <sub> [`00006_WGANGP_MMG_MASS_ROI`](https://medigan.readthedocs.io/en/latest/models.html#wgangp-mmg-mass-roi) </sub>              |     <sub>[Zenodo (6554713)](https://doi.org/10.5281/zenodo.6554713) </sub>      |  <sub>[Szafranowska et al (2022)](https://doi.org/10.48550/arXiv.2203.04961) </sub>  | 
| <sub> Brain Tumors on Flair, T1, T1c, T2 with Masks  </sub> |   <sub>  brain MRI  </sub>    | <sub>   inpaint GAN    </sub> |  <sub> 256x256 </sub>   |       <sub>    [BRATS 2018](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=37224922)     </sub>        | ![sample](docs/source/_static/samples/00007_F.png) <br> ![sample](docs/source/_static/samples/00007_T1.png) <br> ![sample](docs/source/_static/samples/00007_T1c.png) <br> ![sample](docs/source/_static/samples/00007_T2.png) <br> ![sample](docs/source/_static/samples/00007_mask.png) <br> ![sample](docs/source/_static/samples/00007_grade_mask.png) |                <sub> [`00007_INPAINT_BRAIN_MRI`](https://medigan.readthedocs.io/en/latest/models.html#inpaint-brain-mri) </sub>                |     <sub> [Zenodo (7041737)](https://doi.org/10.5281/zenodo.7041737) </sub>     |           <sub>[Kim et al (2020)](https://doi.org/10.1002/mp.14701) </sub>           | 
| <sub> Breast Mass (Mal/Benign)    </sub>                    |  <sub>  mammography  </sub>   |  <sub>   c-dcgan     </sub>   |  <sub> 128x128 </sub>   |              <sub>    [CBIS-DDSM](https://wiki.cancerimagingarchive.net/display/Public/CBIS-DDSM)     </sub>               |                                                                                                                                                      ![sample](docs/source/_static/samples/00008.png)                                                                                                                                                      |               <sub> [`00008_C-DCGAN_MMG_MASSES`](https://medigan.readthedocs.io/en/latest/models.html#c-dcgan-mmg-masses) </sub>               |     <sub>[Zenodo (6647349)](https://doi.org/10.5281/zenodo.6647349) </sub>      |  <sub>[Osuala et al (2024)](https://doi.org/10.48550/arXiv.2407.12669) </sub>                                                                                  |  
| <sub> Polyp with Mask             </sub>                    |   <sub>  endoscopy  </sub>    |    <sub>   pggan   </sub>     |  <sub> 256x256 </sub>   |                                  <sub>    [HyperKvasir](https://osf.io/mh9sj/)     </sub>                                  |                                                                                                                        ![sample](docs/source/_static/samples/00009.png) <br> ![sample](docs/source/_static/samples/00009_mask.png)                                                                                                                         |      <sub> [`00009_PGGAN_POLYP_PATCHES_W_MASKS`](https://medigan.readthedocs.io/en/latest/models.html#pggan-polyp-patches-w-masks) </sub>      |     <sub>[Zenodo (6653743)](https://doi.org/10.5281/zenodo.6653743) </sub>      | <sub>[Thambawita et al (2022)](https://doi.org/10.1371/journal.pone.0267976) </sub>  | 
| <sub> Polyp with Mask             </sub>                    |   <sub>  endoscopy  </sub>    |    <sub>   fastgan </sub>     |  <sub> 256x256 </sub>   |                                  <sub>    [HyperKvasir](https://osf.io/mh9sj/)     </sub>                                  |                                                                                                                        ![sample](docs/source/_static/samples/00010.png) <br> ![sample](docs/source/_static/samples/00010_mask.png)                                                                                                                         |    <sub> [`00010_FASTGAN_POLYP_PATCHES_W_MASKS`](https://medigan.readthedocs.io/en/latest/models.html#fastgan-polyp-patches-w-masks) </sub>    |     <sub>[Zenodo (6660711)](https://doi.org/10.5281/zenodo.6660711) </sub>      | <sub>[Thambawita et al (2022)](https://doi.org/10.1371/journal.pone.0267976) </sub>  | 
| <sub> Polyp with Mask             </sub>                    |   <sub>  endoscopy  </sub>    |     <sub>   singan </sub>     |  <sub> ≈250x250 </sub>  |                                  <sub>    [HyperKvasir](https://osf.io/mh9sj/)     </sub>                                  |                                                                                                                        ![sample](docs/source/_static/samples/00011.png) <br> ![sample](docs/source/_static/samples/00011_mask.png)                                                                                                                         |     <sub> [`00011_SINGAN_POLYP_PATCHES_W_MASKS`](https://medigan.readthedocs.io/en/latest/models.html#singan-polyp-patches-w-masks) </sub>     |     <sub>[Zenodo (6667944)](https://doi.org/10.5281/zenodo.6667944) </sub>      | <sub>[Thambawita et al (2022)](https://doi.org/10.1371/journal.pone.0267976) </sub>  | 
| <sub> Breast Mass (Mal/Benign)    </sub>                    |  <sub>  mammography  </sub>   |  <sub>   c-dcgan     </sub>   |  <sub> 128x128 </sub>   |                               <sub>    [BCDR](https://bcdr.eu/information/about)     </sub>                                |                                                                                                                                                      ![sample](docs/source/_static/samples/00012.png)                                                                                                                                                      |                      <sub> [`00012_C-DCGAN_MMG_MASSES`](https://medigan.readthedocs.io/en/latest/models.html#id2) </sub>                       |     <sub>[Zenodo (6755693)](https://doi.org/10.5281/zenodo.6818095) </sub>      |                                                                                      | 
| <sub> Breast Density Transfer MLO </sub>                    |  <sub>  mammography  </sub>   |   <sub>   cyclegan   </sub>   |  <sub>1332x800 </sub>   |                          <sub>    [OPTIMAM](https://doi.org/10.48550/arXiv.2004.04742)     </sub>                          |                                                                                                                                                      ![sample](docs/source/_static/samples/00013.png)                                                                                                                                                      | <sub> [`00013_CYCLEGAN_MMG_DENSITY_OPTIMAM_MLO`](https://medigan.readthedocs.io/en/latest/models.html#cyclegan-mmg-density-optimam-mlo) </sub> |     <sub>[Zenodo (6818095)](https://doi.org/10.5281/zenodo.6818095) </sub>      |   <sub> [Garrucho et al (2022)](https://doi.org/10.48550/arXiv.2209.09809) </sub>    | 
| <sub> Breast Density Transfer CC  </sub>                    |  <sub>  mammography  </sub>   |   <sub>   cyclegan   </sub>   |  <sub>1332x800 </sub>   |                          <sub>    [OPTIMAM](https://doi.org/10.48550/arXiv.2004.04742)     </sub>                          |                                                                                                                                                      ![sample](docs/source/_static/samples/00014.png)                                                                                                                                                      |  <sub> [`00014_CYCLEGAN_MMG_DENSITY_OPTIMAM_CC`](https://medigan.readthedocs.io/en/latest/models.html#cyclegan-mmg-density-optimam-cc) </sub>  |     <sub>[Zenodo (6818103)](https://doi.org/10.5281/zenodo.6818103) </sub>      |   <sub> [Garrucho et al (2022)](https://doi.org/10.48550/arXiv.2209.09809) </sub>    |  
| <sub> Breast Density Transfer MLO </sub>                    |  <sub>  mammography  </sub>   |   <sub>   cyclegan   </sub>   |  <sub>1332x800 </sub>   |                  <sub>    [CSAW](https://link.springer.com/article/10.1007/s10278-019-00278-0)     </sub>                  |                                                                                                                                                      ![sample](docs/source/_static/samples/00015.png)                                                                                                                                                      |    <sub> [`00015_CYCLEGAN_MMG_DENSITY_CSAW_MLO`](https://medigan.readthedocs.io/en/latest/models.html#cyclegan-mmg-density-csaw-mlo) </sub>    |     <sub>[Zenodo (6818105)](https://doi.org/10.5281/zenodo.6818105) </sub>      |   <sub> [Garrucho et al (2022)](https://doi.org/10.48550/arXiv.2209.09809) </sub>    |  
| <sub> Breast Density Transfer CC  </sub>                    |  <sub>  mammography  </sub>   |   <sub>   cyclegan   </sub>   |  <sub>1332x800 </sub>   |                  <sub>    [CSAW](https://link.springer.com/article/10.1007/s10278-019-00278-0)    </sub>                   |                                                                                                                                                      ![sample](docs/source/_static/samples/00016.png)                                                                                                                                                      |     <sub> [`00016_CYCLEGAN_MMG_DENSITY_CSAW_CC`](https://medigan.readthedocs.io/en/latest/models.html#cyclegan-mmg-density-csaw-cc) </sub>     |     <sub>[Zenodo (6818107)](https://doi.org/10.5281/zenodo.6818107) </sub>      |   <sub> [Garrucho et al (2022)](https://doi.org/10.48550/arXiv.2209.09809) </sub>    | 
| <sub> Lung Nodules                </sub>                    |  <sub>  chest x-ray  </sub>   |   <sub>   dcgan      </sub>   |  <sub>128x128  </sub>   |                        <sub>    [NODE21](https://zenodo.org/record/4725881#.YxNmNuxBwXA)     </sub>                        |                                                                                                                                                      ![sample](docs/source/_static/samples/00017.png)                                                                                                                                                      |          <sub> [`00017_DCGAN_XRAY_LUNG_NODULES`](https://medigan.readthedocs.io/en/latest/models.html#dcgan-xray-lung-nodules) </sub>          |     <sub>[Zenodo (6943691)](https://doi.org/10.5281/zenodo.6943691) </sub>      |                                                                                      | 
| <sub> Lung Nodules                </sub>                    |  <sub>  chest x-ray  </sub>   |  <sub>   wgan-gp      </sub>  |  <sub>128x128  </sub>   |                        <sub>    [NODE21](https://zenodo.org/record/4725881#.YxNmNuxBwXA)     </sub>                        |                                                                                                                                                      ![sample](docs/source/_static/samples/00018.png)                                                                                                                                                      |         <sub> [`00018_WGANGP_XRAY_LUNG_NODULES`](https://medigan.readthedocs.io/en/latest/models.html#wgangp-xray-lung-nodules) </sub>         |     <sub>[Zenodo (6943761)](https://doi.org/10.5281/zenodo.6943761) </sub>      |                                                                                      | 
| <sub> Chest Xray Images           </sub>                    |  <sub>  chest x-ray  </sub>   |   <sub>   pggan      </sub>   | <sub>1024x1024  </sub>  |             <sub>    [ChestX-ray14](https://nihcc.app.box.com/v/ChestXray-NIHCC/folder/36938765345)     </sub>             |                                                                                                                                                      ![sample](docs/source/_static/samples/00019.png)                                                                                                                                                      |                 <sub> [`00019_PGGAN_CHEST_XRAY`](https://medigan.readthedocs.io/en/latest/models.html#pggan-chest-xray) </sub>                 |     <sub>[Zenodo (6943803)](https://doi.org/10.5281/zenodo.6943803) </sub>      |                                                                                      | 
| <sub> Chest Xray Images           </sub>                    |  <sub>  chest x-ray  </sub>   |   <sub>   pggan      </sub>   | <sub>1024x1024  </sub>  |             <sub>    [ChestX-ray14](https://nihcc.app.box.com/v/ChestXray-NIHCC/folder/36938765345)     </sub>             |                                                                                                                                                      ![sample](docs/source/_static/samples/00020.png)                                                                                                                                                      |                       <sub> [`00020_PGGAN_CHEST_XRAY`](https://medigan.readthedocs.io/en/latest/models.html#id3) </sub>                        |     <sub>[Zenodo (7046280)](https://doi.org/10.5281/zenodo.7046280) </sub>      |    <sub> [Segal et al (2021)](https://doi.org/10.1007/s42979-021-00720-7) </sub>     |
| <sub> Brain T1-T2 MRI Modality Transfer </sub>              |   <sub>  brain MRI  </sub>    | <sub>   cyclegan      </sub>  |  <sub>224x192  </sub>   |                           <sub>    [CrossMoDA 2021](https://arxiv.org/abs/2201.02831)     </sub>                           |                                                                                                                                                      ![sample](docs/source/_static/samples/00021.png)                                                                                                                                                      |         <sub> [`00021_CYCLEGAN_BRAIN_MRI_T1_T2`](https://medigan.readthedocs.io/en/latest/models.html#cyclegan-brain-mri-t1-t2) </sub>         |     <sub>[Zenodo (7074555)](https://doi.org/10.5281/zenodo.7074555) </sub>      |   <sub> [Joshi et al (2022)](https://doi.org/10.1007/978-3-031-09002-8_47) </sub>    |
| <sub> Cardiac MRI Age Transfer </sub>                       |  <sub>  cardiac MRI  </sub>   |   <sub>   wgan      </sub>    |  <sub>256x256  </sub>   |                               <sub>    [UK Biobank](https://www.ukbiobank.ac.uk/)     </sub>                               |                                                                                                                                                      ![sample](docs/source/_static/samples/00022.png)                                                                                                                                                      |               <sub> [`00022_WGAN_CARDIAC_AGING`](https://medigan.readthedocs.io/en/latest/models.html#wgan-cardiac-aging) </sub>               |     <sub>[Zenodo (7446930)](https://doi.org/10.5281/zenodo.74469305) </sub>     |    <sub> [Campello et al (2022)](https://doi.org/10.3389/fcvm.2022.983091) </sub>    |
| <sub> Breast DCE-MRI Contrast Injection </sub>              | <sub>  breast DCE-MRI  </sub> | <sub>   pix2pixHD      </sub> | <sub>512x512  </sub>    | <sub>    [Duke Dataset](https://sites.duke.edu/mazurowski/resources/breast-cancer-mri-dataset/)     </sub>                 |                                                                                                                                                      ![sample](docs/source/_static/samples/00023.png)                                                                                                                                                      |          <sub> [`00023_PIX2PIXHD_BREAST_DCEMRI`](https://medigan.readthedocs.io/en/latest/models.html#pix2pixhd-breast-dcemri) </sub>          | <sub>[Zenodo (10210944)](https://zenodo.org/doi/10.5281/zenodo.10210944) </sub> |    <sub> [Osuala et al (2023)](https://doi.org/10.48550/arXiv.2311.10879) </sub>     |

Model information can be found in:
- [model documentation](https://medigan.readthedocs.io/en/latest/models.html) (e.g. the parameters of the models' generate functions)
- [global.json](https://github.com/RichardObi/medigan/blob/main/config/global.json) file (e.g. metadata for model description, selection, and execution)
- [medigan paper](https://arxiv.org/abs/2209.14472) (e.g. analysis and comparisons of models and FID scores)

## Installation
To install the current release, simply run:
```console
pip install medigan
```
Or, alternatively via conda:
```console
conda install -c conda-forge medigan
```

## Getting Started
Examples and notebooks are located at [examples](examples) folder

Documentation is available at [medigan.readthedocs.io](https://medigan.readthedocs.io/en/latest/)


### Generation example
#### DCGAN 
Create mammography masses with labels (malignant or benign) using a [class-conditional DCGAN model](https://arxiv.org/abs/2407.12669).
```python
# import medigan and initialize Generators
from medigan import Generators
generators = Generators()

# generate 8 samples with model 8 (00008_C-DCGAN_MMG_MASSES). 
# Also, auto-install required model dependencies.
generators.generate(model_id=8, num_samples=8, install_dependencies=True)
```
![sample](docs/source/_static/samples/c-dcgan/model8_samples.png)

The synthetic images in the top row show malignant masses (breast cancer) while the images in the bottom row show benign masses. 
Given such images with class information, [image classification models](https://arxiv.org/abs/2407.12669) can be (pre-)trained.


#### CYCLEGAN 
Create mammograms translated from Low-to-High Breast Density using CYCLEGAN model
```python
from medigan import Generators
generators = Generators()
# model 3 is "00003_CYCLEGAN_MMG_DENSITY_FULL"
generators.generate(model_id=3, num_samples=1)
```
![sample](docs/source/_static/samples/cyclegan/sample_image_5_low.png)
&rarr;
![sample](docs/source/_static/samples/cyclegan/sample_image_5_high.png)


### Search Example
Search for a [model](https://medigan.readthedocs.io/en/latest/models.html) inside medigan using keywords
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
# model 4 is "00004_PIX2PIX_MMG_MASSES_W_MASKS"
dataloader = generators.get_as_torch_dataloader(model_id=4, num_samples=3)
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
```python
from medigan import Generators

generators = Generators()
# model 10 is "00010_FASTGAN_POLYP_PATCHES_W_MASKS"
generators.visualize(10)
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

## Reference

If you use a medigan model in your work, please cite its respective publication ([see references](#available-models)). 

Please also consider citing the medigan paper:

> [Osuala, R., Skorupko, G., Lazrak, N., Garrucho, L., García, E., Joshi, S., ... & Lekadir, K. (2023). medigan: a Python library of pretrained generative models for medical image synthesis. Journal of Medical Imaging, 10(6), 061403.](https://doi.org/10.1117/1.JMI.10.6.061403)

BibTeX entry:
```bibtex
@article{osuala2023medigan,
  title={medigan: a Python library of pretrained generative models for medical image synthesis},
  author={Osuala, Richard and Skorupko, Grzegorz and Lazrak, Noussair and Garrucho, Lidia and Garc{\'\i}a, Eloy and Joshi, Smriti and Jouide, Socayna and Rutherford, Michael and Prior, Fred and Kushibar, Kaisar and others},
  journal={Journal of Medical Imaging},
  volume={10},
  number={6},
  pages={061403},
  year={2023},
  publisher={SPIE}
}
```
