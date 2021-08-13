# -*- coding: utf-8 -*-
#! /usr/bin/env python
"""
@author: Richard Osuala, Noussair Lazrak
BCN-AIM Lab 2021
Contact: richard.osuala@ub.edu
"""

# TODO Move this to ../tests/tests.py
# run with python -m src.medigan.main


from __future__ import absolute_import
from .generators import Generators


def main():
    generators = Generators()
    generators.generate(model_id="2d29d505-9fb7-4c4d-b81f-47976e2c7dbf", number_of_images=3)
    generators.generate(model_id="8f933c5e-72fc-461a-a5cb-73cbe65af6fc", number_of_images=3)

if __name__ == "__main__": main()
