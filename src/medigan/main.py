# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""
@author: Richard Osuala
BCN-AIM Lab 2021
Contact: richard.osuala@ub.edu
"""

# TODO Move this to ../tests/tests.py
# run with python -m src.medigan.main

from __future__ import absolute_import

from .generators import Generators


def main():
    generators = Generators()

    # model generation tests
    model_generation_test(generators)

    # quit()

    # model selection tests
    model_selection_test(generators)

    # print tests
    print_tests(generators)


def model_generation_test(generators):
    generators.generate(model_id="2d29d505-9fb7-4c4d-b81f-47976e2c7dbf", number_of_images=3)
    generators.generate(model_id="8f933c5e-72fc-461a-a5cb-73cbe65af6fc", number_of_images=3)


def print_tests(generators):
    print(generators)
    print(' ------------------------------------------------ ')
    print(generators.model_selector)
    print(' ------------------------------------------------ ')
    generators.add_all_model_executors()
    print(generators.model_executors)
    print(' ------------------------------------------------ ')
    print(generators.model_executors[0])
    print(' ------------------------------------------------ ')
    print(generators.config_manager)


def model_selection_test(generators):
    values_list = ['dcgan', 'mMg', 'ClF', 'modalities', 'inbreast']
    models = generators.find_matching_models_by_values(values=values_list, target_values_operator='AND',
                                                       are_keys_also_matched=True, is_case_sensitive=False)
    print(f'THESE MODELS WERE FOUND: {models}')
    print(models[0][0])
    print(models)


if __name__ == "__main__": main()
