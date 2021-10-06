Description
==============

.. contents:: Table of Contents


Aim and Scope
_______________

`medigan` focuses on automating medical image dataset synthesis using GANs.

These datasets can again be used to train diagnostic or prognostic clinical models such as disease classification, detection and segmentation models.

Despite this current focus, medigan, is readily extendable to any type of modality and any type of generative model.

Core Features
_______________

    - Researchers and ML-practitioners can conveniently use an existing model in `medigan` for synthetic data augmentation instead of having to train their own generative model each time.

    - Users can search and find a model using search terms (e.g. "Mammography, 128x128, DCGAN") or key value pairs (e.g. `key` = "modality", `value` = "Mammography")

    - Users can explore the config and information (metrics, use-cases, modalities, etc) of each model in `medigan`

    - Users can generate samples using a model

    - Users can also get the generate_method of a model that they may want to use dynamically inside their dataloaders

Adding Models to medigan
___________________________

    - `medigan` motivates the reuse of trained generative models.

    - Models can be added via pull request by adding a model to the `config <https://github.com/RichardObi/medigan-models>`_

        - This link is also stored in `medigan.constants.CONFIG_FILE_URL`.

    - Model contributors need to specify a link to their model package in the config. We recommend to host and link model pack`ages on Zenodo. Reasons:

        - Zenodo model packages get a static DOI. This provides clarity as to who the contributors and IP owners of each generative model in `medigan` are.

        - File modification/updates under the same DOI are not possible in Zenodo. This helps to avoid security issues as package content remains static after the model is tested, verified, and added to `medigan`.

        - Examples of how `medigan` model packages should be hosted on Zenodo can be found `here <https://doi.org/10.5281/zenodo.5187714>`_ (model_id: 00001_DCGAN_MMG_CALC_ROI), `here <https://doi.org/10.5281/zenodo.5188557>`_ (model_id: 00002_DCGAN_MMG_MASS_ROI), and `here <https://doi.org/10.5281/zenodo.5547263>`_ (model id: 00003_CYCLEGAN_MMG_DENSITY_FULL).

Links
___________________________
- `Github (medigan library) <https://github.com/RichardObi/medigan>`_
- `Github (medigan config) <https://github.com/RichardObi/medigan-models>`_
- `Test Pypi (medigan library) <https://test.pypi.org/project/medigan/>`_