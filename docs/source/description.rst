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

    - Model contributors can share and disseminate their generative models thereby augmenting their reach.


Architecture and Workflows
___________________________

.. figure:: _static/medigan-workflows.png
   :alt: Architectural overview and main workflows

   Architectural overview including main workflows consisting of (a) library import and initialisation, (b) generative model search and ranking, (c) sample generation, and (d) generative model contribution.


Issues
_______________
In case you encounter problems while using `medigan` or would like to request additional features, please create a `new issue <https://github.com/RichardObi/medigan/issues>`_ and we will try to help.


Links
___________________________
- `Github (medigan library) <https://github.com/RichardObi/medigan>`_
- `Github (medigan config) <https://github.com/RichardObi/medigan-models>`_
- `Test Pypi (medigan library) <https://test.pypi.org/project/medigan/>`_