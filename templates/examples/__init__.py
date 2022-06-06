"""
authors: Richard Osuala, Zuzanna Szafranowska
BCN-AIM 2021
"""

import logging
import os
from pathlib import Path

import cv2
import numpy as np
import torch


import torch
import torch.nn as nn
import torch.nn.parallel
import logging


class BaseGenerator(nn.Module):
    def __init__(
        self,
        nz: int,
        ngf: int,
        nc: int,
        ngpu: int,
        leakiness: float = 0.2,
        bias: bool = False,
    ):
        super(BaseGenerator, self).__init__()
        self.nz = nz
        self.ngf = ngf
        self.nc = nc
        self.ngpu = ngpu
        self.leakiness = leakiness
        self.bias = bias
        self.main = None

    def forward(self, input):
        raise NotImplementedError


class Generator(BaseGenerator):
    def __init__(
        self,
        nz: int,
        ngf: int,
        nc: int,
        ngpu: int,
        image_size: int,
        conditional: bool,
        leakiness: float,
        bias: bool = False,
        n_cond: int = 10,
        is_condition_categorical: bool = False,
        num_embedding_dimensions: int = 50
    ):
        super(Generator, self).__init__(
            nz=nz,
            ngf=ngf,
            nc=nc,
            ngpu=ngpu,
            leakiness=leakiness,
            bias=bias,
        )
        # if is_condition_categorical is False, we model the condition as continous input to the network
        self.is_condition_categorical = is_condition_categorical

        # n_cond is only used if is_condition_categorical is True.
        self.num_embedding_input = n_cond

        # num_embedding_dimensions is only used if is_condition_categorical is True.
        # num_embedding_dimensions standard would be dim(z), but atm we have a nn.Linear after
        # nn.Embedding that upscales the dimension to self.nz. Using same value of num_embedding_dims in D and G.
        self.num_embedding_dimensions = num_embedding_dimensions

        # whether the is a conditional input into the GAN i.e. cGAN
        self.conditional: bool = conditional

        # The image size (supported params should be 128 or 64)
        self.image_size = image_size

        if self.image_size == 128:
            self.first_layers = nn.Sequential(
                # input is Z, going into a convolution
                nn.ConvTranspose2d(self.nz * self.nc, self.ngf * 16, 4, 1, 0, bias=self.bias),
                nn.BatchNorm2d(self.ngf * 16),
                nn.ReLU(True),
                # state size. (ngf*16) x 4 x 4
                nn.ConvTranspose2d(self.ngf * 16, self.ngf * 8, 4, 2, 1, bias=self.bias),
                nn.BatchNorm2d(self.ngf * 8),
                nn.ReLU(True),
            )
        elif self.image_size == 64:
            self.first_layers = nn.Sequential(
                # input is Z, going into a convolution
                nn.ConvTranspose2d(self.nz * self.nc, self.ngf * 8, 4, 1, 0, bias=self.bias),
                nn.BatchNorm2d(self.ngf * 8),
                nn.ReLU(True),
            )
        else:
            raise ValueError(f"Allowed image sizes are 128 and 64. You provided {self.image_size}. Please adjust.")

        self.main = nn.Sequential(
            *self.first_layers.children(),
            # state size. (ngf*8) x 8 x 8
            nn.ConvTranspose2d(self.ngf * 8, self.ngf * 4, 4, 2, 1, bias=self.bias),
            nn.BatchNorm2d(self.ngf * 4),
            nn.ReLU(True),
            # state size. (ngf*4) x 16 x 16
            nn.ConvTranspose2d(self.ngf * 4, self.ngf * 2, 4, 2, 1, bias=self.bias),
            nn.BatchNorm2d(self.ngf * 2),
            nn.ReLU(True),
            # state size. (ngf*2) x 32 x 32
            nn.ConvTranspose2d(self.ngf * 2, self.ngf, 4, 2, 1, bias=self.bias),
            nn.BatchNorm2d(self.ngf),
            nn.ReLU(True),
            # state size. (ngf) x 64 x 64
            # Note that out_channels=1 instead of out_channels=self.nc.
            # This is due to conditional input channel of our grayscale images
            nn.ConvTranspose2d(in_channels=self.ngf, out_channels=1, kernel_size=4, stride=2, padding=1,
                               bias=self.bias),
            nn.Tanh()
            # state size. (nc) x 128 x 128
        )

        if self.is_condition_categorical:
            self.embed_nn = nn.Sequential(
                # e.g. condition -> int -> embedding -> fcl -> feature map -> concat with image -> conv layers..
                # embedding layer
                nn.Embedding(
                    num_embeddings=self.num_embedding_input,
                    embedding_dim=self.num_embedding_dimensions,
                ),
                # target output dim of dense layer is batch_size x self.nz x 1 x 1
                # input is dimension of the embedding layer output
                nn.Linear(in_features=self.num_embedding_dimensions, out_features=self.nz),
                # nn.BatchNorm1d(self.nz),
                nn.LeakyReLU(self.leakiness, inplace=True),
            )
        else:
            self.embed_nn = nn.Sequential(
                # target output dim of dense layer is: nz x 1 x 1
                # input is dimension of the numbers of embedding
                nn.Linear(in_features=1, out_features=self.nz),
                # TODO Ablation: How does BatchNorm1d affect the conditional model performance?
                nn.BatchNorm1d(self.nz),
                nn.LeakyReLU(self.leakiness, inplace=True),
            )

    def forward(self, x, conditions=None):
        if self.conditional:
            # combining condition labels and input images via a new image channel
            if not self.is_condition_categorical:
                # If labels are continuous (not modelled as categorical), use floats instead of integers for labels.
                # Also adjust dimensions to (batch_size x 1) as needed for input into linear layer
                # labels should already be of type float, no change expected in .float() conversion (it is only a safety check)

                # Just for testing:
                conditions *= 0
                conditions += 1

                conditions = conditions.view(conditions.size(0), -1).float()
            embedded_conditions = self.embed_nn(conditions)
            embedded_conditions_with_random_noise_dim = embedded_conditions.view(-1, self.nz, 1, 1)
            x = torch.cat([x, embedded_conditions_with_random_noise_dim], 1)
        return self.main(x)

def interval_mapping(image, from_min, from_max, to_min, to_max):
    # map values from [from_min, from_max] to [to_min, to_max]
    # image: input array
    from_range = from_max - from_min
    to_range = to_max - to_min
    # scale to interval [0,1]
    scaled = np.array((image - from_min) / float(from_range), dtype=float)
    # multiply by range and add minimum to get interval [min,range+min]
    return to_min + (scaled * to_range)


def image_generator(model_path, device, nz, ngf, nc, ngpu, num_samples):
    # instantiate the model
    logging.debug("Instantiating model...")
    netG = Generator(
        nz=nz,
        ngf=ngf,
        nc=nc,
        ngpu=ngpu,
        image_size=128,
        leakiness=0.1,
        conditional=False,
    )
    if device.type == "cuda":
        netG.cuda()

    # load the model's weights from state_dict *'.pt file
    logging.debug(f"Loading model weights from {model_path} ...")

    checkpoint = torch.load(model_path, map_location=device)
    try:
        netG.load_state_dict(state_dict=checkpoint["generator"])
    except KeyError:
        raise KeyError(f"checkpoint['generator_state_dict'] was not found.") #checkpoint={checkpoint}")
    logging.debug(f'Using retrieved model from generator_state_dict checkpoint')
    netG.eval()

    # generate the images
    logging.debug(f"Generating {num_samples} images using {device}...")
    z = torch.randn(num_samples, nz, 1, 1, device=device)
    images = netG(z).detach().cpu().numpy()
    image_list = []
    for j, img_ in enumerate(images):
        image_list.append(img_)
    return image_list


def save_generated_images(image_list, path):
    logging.debug(f"Saving generated images now in {path}")
    for i, img_ in enumerate(image_list):
        Path(path).mkdir(parents=True, exist_ok=True)
        img_path = f"{path}/{i}.png"
        img_ = interval_mapping(img_.transpose(1, 2, 0), -1.0, 0.0, 0, 255)
        img_ = img_.astype("uint8")
        cv2.imwrite(img_path, img_)
    logging.debug(f"Saved generated images to {path}")


def return_images(image_list):
    #logging.debug(f"Returning generated images as {type(image_list)}.")
    processed_image_list = []
    for i, img_ in enumerate(image_list):
        img_ = interval_mapping(img_.transpose(1, 2, 0), -1.0, 0.0, 0, 255)
        img_ = img_.astype("uint8")
        processed_image_list.append(img_)
    return processed_image_list


def generate(model_file, num_samples, output_path, save_images: bool):
    """ This function generates synthetic images of mammography regions of interest """
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        ngpu = 0
        if device == "cuda":
            ngpu = 1
        image_list = image_generator(model_file, device, 100, 64, 1, ngpu, num_samples)
        if save_images:
            save_generated_images(image_list, output_path)
        else:
            return return_images(image_list)
    except Exception as e:
        logging.error(f"Error while trying to generate {num_samples} images with model {model_file}: {e}")
        raise e

