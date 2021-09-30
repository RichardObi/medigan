# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" main script used to test the functions of the medigan module.

.. codeauthor:: Richard Osuala <richard.osuala@gmail.com>
.. codeauthor:: Noussair Lazrak <lazrak.noussair@gmail.com>
"""
import logging
import sys
import numpy

from src.medigan.generators import Generators


# Note: The below tests were moved to unittest class in ../tests/tests.py
# run with python -m tests.main

def main():
    # This logger on root level initialized via logging.getLogger() will also log all log events
    # from the medigan library. Pass a logger name (e.g. __name__) instead if you only want logs from tests.py
    logger = logging.getLogger()  # (__name__)
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    generators = Generators()
    # quit()

    # TEST: model generation
    model_generation_test(generators)

    # TEST: return a generate() function and test it's usage
    # model_return_generate_function(generators)

    # TEST: model selection
    # model_selection_test(generators)

    # TEST: print
    # print_tests(generators)

    # TEST: finding the model and generation with found model
    # find_model_and_generate_test(generators)

    # TEST: rank the models by performance
    # rank_models_by_performance_test(generators)

    # TEST: find models first by search values and then rank the models by performance
    # find_and_rank_models_by_performance(generators)

    # TEST: find the models, rank the models by performance, generated with highest ranked
    # find_and_rank_models_then_generate_test(generators)

    # TEST: get the models by key value pair
    # get_models_by_key_value_pair(generators)


def model_generation_test(generators):
    images1 = generators.generate(model_id="00001_DCGAN_MMG_CALC_ROI", num_samples=3, save_images=False)
    #logging.info(f"images1: {images1}")
    images2 = generators.generate(model_id="00002_DCGAN_MMG_MASS_ROI", num_samples=3, save_images=False)
    #logging.info(f"images2: {images2}")
    ## generators.generate(model_id="00001_DCGAN_MMG_CALC_ROI", num_samples=3, **{"test": "this is my test"})

    #generate_method = generators.get_generate_function(model_id="00001_DCGAN_MMG_CALC_ROI", num_samples=3, save_images=False)
    #images1 = generate_method()
    #logging.info(f"images1: {images1}")


def model_return_generate_function(generators):
    gen_function = generators.get_generate_function(model_id="00001_DCGAN_MMG_CALC_ROI", num_samples=3)
    print("I now generate 1 !!")
    gen_function()
    print("I now generate 2 !!")
    gen_function(**{"test2": "abcdefghijklmnopqrstuvwxyz"})
    print("I now generate 3 !!")
    # generators.generate(model_id="00002_DCGAN_MMG_MASS_ROI", num_samples=3)


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
    values_list = ['dcgan', 'mMg', 'ClF', 'modalities']
    models = generators.find_matching_models_by_values(values=values_list, target_values_operator='AND',
                                                       are_keys_also_matched=True, is_case_sensitive=False)
    print(f'THESE MODELS WERE FOUND: {models}')
    print(models[0][0])
    print(models)


def find_model_and_generate_test(generators):
    values_list = ['dcgan', 'mMg', 'ClF', 'modalities', 'inbreast']
    generators.find_model_and_generate(values=values_list, target_values_operator='AND', are_keys_also_matched=True,
                                       is_case_sensitive=False, num_samples=5)
    values_list = ['dcgan', 'mMg', 'ClF', 'modalities']
    generators.find_model_and_generate(values=values_list, target_values_operator='AND', are_keys_also_matched=True,
                                       is_case_sensitive=False, num_samples=5)

    values_list = ['dcgan', 'mMg', 'ClF', 'inbreast', 'optimam']
    generators.find_model_and_generate(values=values_list, target_values_operator='AND', are_keys_also_matched=True,
                                       is_case_sensitive=False, num_samples=5)


# TODO ADD THIS to tests/tests.py
def rank_models_by_performance_test(generators):
    ranked_models = generators.rank_models_by_performance(metric="SSIM", order="asc")
    print(ranked_models)
    print("                      ---------                      ")

    ranked_models = generators.rank_models_by_performance(metric="SSIM", order="desc")
    print(ranked_models)
    print("                      ---------                      ")

    ranked_models = generators.rank_models_by_performance(
        model_ids=["00001_DCGAN_MMG_CALC_ROI", "00002_DCGAN_MMG_MASS_ROI"], metric="SSIM",
        order="asc")
    print(ranked_models)
    print("                      ---------                      ")

    ranked_models = generators.rank_models_by_performance(metric="downstream_task.CLF.trained on fake.f1", order="asc")
    print(ranked_models)
    print("                      ---------                      ")

    ranked_models = generators.rank_models_by_performance(metric="downstream_task.CLF.trained on fake.accuracy",
                                                          order="asc")
    print(ranked_models)


# TODO ADD THIS to tests/tests.py
def find_and_rank_models_by_performance(generators):
    values_list = ['dcgan', 'MMG']  # , 'inbreast']
    print("                      ---------                      ")
    ranked_models = generators.find_models_and_rank(values=values_list, target_values_operator='AND',
                                                    are_keys_also_matched=True,
                                                    is_case_sensitive=False, metric="SSIM", order="asc")
    print(ranked_models)

    print("                      ---------                      ")
    ranked_models = generators.find_models_and_rank(values=values_list, target_values_operator='AND',
                                                    are_keys_also_matched=True,
                                                    is_case_sensitive=False, metric="SSIM", order="desc")
    print(ranked_models)

    values_list = ['dcgan', 'MMG', 'inbreast']
    print("                      ---------                      ")
    ranked_models = generators.find_models_and_rank(values=values_list, target_values_operator='AND',
                                                    are_keys_also_matched=True,
                                                    is_case_sensitive=False, metric="SSIM", order="asc")
    print(ranked_models)


def find_and_rank_models_then_generate_test(generators):
    values_list = ['dcgan', 'MMG']  # , 'inbreast']
    generators.find_models_rank_and_generate(values=values_list, target_values_operator='AND',
                                             are_keys_also_matched=True,
                                             is_case_sensitive=False, metric="SSIM", order="asc", num_samples=5)
    print("                      ---------                      ")
    generators.find_models_rank_and_generate(values=values_list, target_values_operator='AND',
                                             are_keys_also_matched=True,
                                             is_case_sensitive=False, metric="SSIM", order="desc", num_samples=5)


# TODO ADD THIS to tests/tests.py
def get_models_by_key_value_pair(generators):
    key1 = "modality"
    value1 = "Full-Field Mammography"
    found_models = generators.get_models_by_key_value_pair(key1=key1, value1=value1, is_case_sensitive=False)
    print(found_models)

    key1 = "license"
    value1 = "MIT"
    found_models = generators.get_models_by_key_value_pair(key1=key1, value1=value1, is_case_sensitive=True)
    print(found_models)

    key1 = "performance.downstream_task.CLF.trained on fake.accuracy"
    value1 = 0.999
    found_models = generators.get_models_by_key_value_pair(key1=key1, value1=value1, is_case_sensitive=True)
    print(found_models)


if __name__ == "__main__": main()
