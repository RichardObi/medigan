# -*- coding: utf-8 -*-
# ! /usr/bin/env python
""" `ModelVisualizer` class providing visualizing corresponding model input and model output changes. """

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, Slider


class ModelVisualizer:
    """`ModelVisualizer` class: Visualises synthetic data through a user interface. Depending on a model,
    it is possible to control the input latent vector values and conditional input.

    Parameters
    ----------
    model_executor: ModelExecutor
        The generative model's executor object
    config: dict
        The config dict containing the model metadata


    Attributes
    ----------
    model_executor: ModelExecutor
        The generative model's executor object
    input_latent_vector_size: int
        Size of the latent vector used as an input for generation
    conditional: bool
        Flag for models with conditional input
    condition: Union[int, float]
        Value of the conditinal input to the model
    max_input_value: float
        Absolute value used for setting latent values input range
    """

    def __init__(self, model_executor, config: None):

        self.model_executor = model_executor
        self.model_id = self.model_executor.model_id
        self.config = config
        self.num_samples = 1
        self.max_input_value = 3
        self.conditional = False
        self.condition = None

        self.input_latent_vector_size = (
            self.model_executor.generate_method_input_latent_vector_size
        )
        if not self.input_latent_vector_size:
            raise ValueError(
                f"{self.model_id}: Visualization of this model is not supported. Reason: This model does not use a random vector 'z' as input, which is needed for visualization. This is determined via the absence of the 'input_latent_vector_size' variable in this model's metadata in config/global.json."
            )

        self.gen_function = self.model_executor.generate(
            num_samples=1,
            save_images=False,
            is_gen_function_returned=True,
        )
        if "condition" in self.model_executor.generate_method_args["custom"]:
            self.conditional = True
            self.condition = self.model_executor.generate_method_args["custom"][
                "condition"
            ]

    def visualize(self, slider_grouper: int = 10, auto_close=False):
        """
        Visualize the model's output. This method is called by the user.
        It opens up a user interface with available controls.

        Parameters
        ----------
        slider_grouper: int
            Number of input parameters to group together within one slider.
        auto_close: bool
            Flag for closing the user interface automatically after time. Used while testing.

        Returns
        -------
        None
        """
        z = np.random.randn(
            self.num_samples, self.input_latent_vector_size, 1, 1
        ).astype(np.float32)

        mask = None

        if self.conditional:
            output = self.gen_function(condition=self.condition, input_latent_vector=z)
        else:
            output = self.gen_function(input_latent_vector=z)

        image, mask = self._unpack_output(output)

        images_to_show = 1
        if mask is not None:
            images_to_show += 1

        fig, ax = plt.subplots(ncols=images_to_show)

        if images_to_show == 1:
            ax.axis("off")
            ax.set_title("Generated image")
            display = ax.imshow(image, cmap="gray", vmin=0, vmax=255)
        if images_to_show == 2:
            ax[0].axis("off")
            ax[0].set_title("Generated image")
            display = ax[0].imshow(image, cmap="gray", vmin=0, vmax=255)
            ax[1].axis("off")
            ax[1].set_title("Generated mask")
            display_mask = ax[1].imshow(mask, cmap="gray", vmin=0, vmax=255)

        fig.suptitle(
            "Model " + self.model_id,
            fontsize=15,
            # fontweight="bold",
        )
        if self.config:
            plt.text(
                x=0.5,
                y=0.88,
                s=self.config["description"]["title"],
                fontsize=8,
                ha="center",
                transform=fig.transFigure,
                wrap=True,
            )
        # adjust the main plot to make room for the sliders
        plt.subplots_adjust(left=0.45, bottom=0.3, top=0.8)

        padding = 0.03
        sliders_x = 0.1
        sliders_y = 0.75
        sliders_width = 0.25
        sliders_height = 0.02
        sliders = []
        row_index = 0

        if self.conditional:
            condition_ax = plt.axes(
                (sliders_x, sliders_y, sliders_width, sliders_height)
            )
            condition_slider = Slider(
                condition_ax,
                None,
                0,
                1,
                valinit=0.0,
                valstep=1,
                initcolor="none",
                # valfmt="%.2f",
            )
            condition_ax.set_title("Input condition: " + output[0][1])
            row_index += 5

        offset_ax = plt.axes(
            (sliders_x, sliders_y - row_index * padding, sliders_width, sliders_height)
        )
        offset_ax.set_title("Input latent vector")
        offset_slider = Slider(
            offset_ax,
            "offset",
            -self.max_input_value * 2,
            self.max_input_value * 2,
            valinit=0.0,
            initcolor="none",
            valfmt="%.2f",
        )
        row_index += 2
        # for i in range(int(self.input_latent_vector_size)):
        for i in range(int(self.input_latent_vector_size / slider_grouper)):
            axfreq = plt.axes(
                (
                    sliders_x,
                    sliders_y - (i + row_index) * padding,
                    sliders_width,
                    sliders_height,
                )
            )
            slider = Slider(
                axfreq,
                "z{}".format(i + 1),
                -self.max_input_value,
                self.max_input_value,
                valinit=float(z[0][i]),
                initcolor="none",
                valfmt="%.2f",
            )
            sliders.append(slider)

        text = "Offset: Add constant value to each latent variable \
             \nInput vector: Modify latent values used to generate image \
              \nSeed: Initialize new random seed for latent vector \
              \nReset: Revert user changes to initial seed values"

        ax_legend = plt.axes(
            (
                0.45,
                0.19,
                0.5,
                0.5,
            )
        )
        ax_legend.axis("off")

        ax_legend.text(0.0, 0.0, text, fontsize=8, va="top", linespacing=2)

        # The function to be called anytime a slider's value changes
        def update(val):
            for i, slider in enumerate(sliders):
                for j in range(10):
                    z[0][i + j] = slider.val

            if self.conditional:
                self.condition = condition_slider.val
                output = self.gen_function(
                    condition=self.condition, input_latent_vector=z
                )
                condition_ax.set_title("Input condition: " + output[0][1])
            else:
                output = self.gen_function(input_latent_vector=z)

            image, mask = self._unpack_output(output)
            if mask is not None:
                display_mask.set_data(mask)
            display.set_data(image)
            fig.canvas.draw_idle()

        # register the update function with each slider
        for slider in sliders:
            slider.on_changed(update)
        if self.conditional:
            condition_slider.on_changed(update)

        self.offset_old = 0

        def update_offset(val):
            diff = offset_slider.val - self.offset_old
            self.offset_old = offset_slider.val

            for i, slider in enumerate(sliders):
                if slider.val + diff > self.max_input_value:
                    slider.set_val(self.max_input_value)
                elif slider.val + diff < -self.max_input_value:
                    slider.set_val(-self.max_input_value)
                else:
                    slider.set_val(slider.val + diff)

                for j in range(10):
                    z[0][i + j] = slider.val

        offset_slider.on_changed(update_offset)

        # Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
        resetax = plt.axes([0.77, 0.220, 0.1, 0.04])
        reset_button = Button(resetax, "Reset", hovercolor="0.975")
        seedax = plt.axes([0.62, 0.220, 0.1, 0.04])
        seed_button = Button(seedax, "Seed", hovercolor="0.975")

        def reset(event):
            offset_slider.reset()
            for slider in sliders:
                slider.reset()

        def new_seed(event):
            z = np.random.randn(
                self.num_samples, self.input_latent_vector_size, 1, 1
            ).astype(np.float32)
            for slider in sliders:
                slider.valinit = z[0][sliders.index(slider)]
            reset(event)

        reset_button.on_clicked(reset)
        seed_button.on_clicked(new_seed)
        update(0)
        if auto_close:
            plt.show(block=False)
            plt.pause(1)
            plt.close()
        else:
            plt.show()

    def _unpack_output(self, output) -> tuple:
        """
        Unpack the output of the generator function

        Parameters
        ----------
        output: Union[tuple, np.ndarray]
            Output of the generator function to unpack into an image and optional mask

        Returns
        ----------
        tuple[image, mask]
            Tuple of the image and mask. Mask is None if no mask was available
        """
        mask = None
        if type(output[0]) is tuple:
            image = output[0][0].squeeze()
            if type(output[0][1]) is not str:
                mask = output[0][1].squeeze()
        else:
            image = output[0].squeeze()

        return image, mask
