
Getting started
================
Let's install `medigan` and generate a few synthetic images.

.. code-block:: Python

    pip install medigan


.. code-block:: Python

    from medigan import Generators
    Generators.generate(model_id="00001_DCGAN_MMG_CALC_ROI")


Workflow
=============
.. figure:: _static/medigan-workflows.png
   :alt: Architectural overview and main workflows

   Architectural overview including main workflows consisting of (a) library import and initialisation, (b) generative model search and ranking, (c) sample generation, and (d) generative model contribution.

.. toctree::
   :caption: Description
   :maxdepth: 3

   description

.. toctree::
   :caption: Code Examples
   :maxdepth: 3

   code_examples

.. toctree::
   :caption: Modules
   :maxdepth: 5

   modules

.. toctree::
   :caption: Tests
   :maxdepth: 5

   tests

.. toctree::
   :caption: Models
   :maxdepth: 5

   models

Indices
=======
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`