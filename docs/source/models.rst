Generative Models
=======================

This section provides an overview of the generative models in `medigan`.

Find in the tables below for each model:

#. A **model_id**
#. A link to detailed documentation on **Zenodo**

Further model information can be found in the `global.json <https://github.com/RichardObi/medigan/blob/main/config/global.json>`_ metadata.

.. warning::
    Some of the model internal checkpoint loading functions may implicitly use the pickle module (e.g. `torch.load() <https://pytorch.org/docs/stable/generated/torch.load.html>`_),
    Pickle is insecure: It is possible to construct malicious pickle data which will execute arbitrary code during unpickling (`example video <https://youtu.be/2ethDz9KnLk>`_).
    While we do our best to analyse and test each model before Zenodo upload and `medigan` integration, we cannot provide a security guarantee. Be aware and run only models you trust.
    To further mitigate risks, we plan to integrate a malware scanning tool into medigan's `CI pipeline <https://pytorch.org/docs/stable/generated/torch.load.html>`_.


.. include:: model_documentation.md
   :parser: myst_parser.sphinx_
