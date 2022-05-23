# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" `medigan` is a modular Python library for automating synthetic dataset generation.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
.. codeauthor:: Noussair Lazrak <lazrak.noussair@gmail.com>
"""
# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler

# importing the generators module and class for the convenience of extending the "medigan.generators" namespace to
# "medigan", allowing 'from medigan import Generators'
from .generators import Generators

logging.getLogger(__name__).addHandler(NullHandler())
