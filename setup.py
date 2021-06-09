import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="medigan",                  
    version="0.0.1",                        
    author="Authors from UB",                     
    description="Quicksample Test Package for medigan Demo",
    long_description=long_description,      
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      
    python_requires='>=2.6',                
    py_modules=["medigan"],             
    package_dir={'':'medigan'},     
    install_requires=["Path","Union","pyyaml","numpy","torch","opencv-contrib-python-headless"]
)
