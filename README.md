
# Medigan lib v1

A sample python package deployment for MediGan ToolBox.
clone this repository, cd into /medigan and install the package locally following the step:

`python -m pip install –-user –-upgrade setuptools wheel`

`python setup.py sdist bdist_wheel`

`pip install -e .`

you can then import medigan to your code an run the foollowing 

`medigan.generate_GAN_images("DCGAN", device, 120, 20,"generated_with_DCGAN")`

