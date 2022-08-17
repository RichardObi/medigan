# coding: utf-8
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="medigan",
    version="0.0.2",
    author="Richard Osuala, Grzegorz Skorupko, Noussair Lazrak",
    description="medigan is a modular open-source Python library that provides an interface to multiple generative models and automates synthetic dataset generation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RichardObi/medigan",
    project_urls={
        "Bug Tracker": "https://github.com/RichardObi/medigan/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=["tqdm", "requests", "torch", "numpy", "PyGithub", "matplotlib"],
)
