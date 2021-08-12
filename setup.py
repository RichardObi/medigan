# coding: utf-8
import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="medigan",                  
    version="0.0.1",
    author="Noussair Lazrak, Richard Osuala, Kaisar Kushibar, Oliver Díaz, Karim Lekadir",                     
    description="MediGAN is a Python library to implement Generative Adversarial Networks(GANs), Conditional GANs, Adversarial Auto-Encoders(AAEs), etc. This library aims to enhance data augmentation via providing/ generating training data sets for other Deep learning models.",
    long_description=long_description,      
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    url="https://github.com/RichardObi/GANtoolbox",
    project_urls={
        "Bug Tracker": "https://github.com/RichardObi/GANtoolbox/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      
    python_requires='>=3.6',
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=["Path","Union","pyyaml","numpy","torch","opencv-contrib-python-headless"]
)
