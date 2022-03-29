This file is Work in Progress
# Contributing

## How to Add New Models to medigan:

- `medigan` motivates the reuse of trained generative models.

- Models can be added via pull request by adding a model to the config in https://github.com/RichardObi/medigan-models (link stored in `medigan.constants.CONFIG_FILE_URL`).

- Model contributors need to specify a link to their model package in the config. We recommend to host and link model packages on Zenodo. Reasons:

    - Zenodo model packages get a static DOI. This provides clarity as to who the contributors and IP owners of each generative model in `medigan` are.

    - File modification/updates under the same DOI are not possible in Zenodo. This helps to avoid security issues as package content remains static after the model is tested, verified, and added to `medigan`.

    - Examples of how `medigan` model packages should be hosted on Zenodo can be found here: https://doi.org/10.5281/zenodo.5187715 and here: https://doi.org/10.5281/zenodo.5188558


## Architectural Overview
![medigan architecture and worklows](docs/source/_static/medigan-workflows.png)
