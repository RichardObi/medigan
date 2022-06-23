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

    def __init__(self, model_executor):

        self.model_executor = model_executor
        self.model_id = self.model_executor.model_id
        self.num_samples = 1
        self.max_input_value = 3
        self.conditional = False
        self.condition = None

        self.input_latent_vector_size = (
            self.model_executor.generate_method_input_latent_vector_size
        )
        if not self.input_latent_vector_size:
            raise ValueError("Visualization of this model is not supported")

        self.gen_function = self.model_executor.generate(
            num_samples=1, save_images=False, is_gen_function_returned=True,
        )
        if "condition" in self.model_executor.generate_method_args["custom"]:
            self.conditional = True
            self.condition = self.model_executor.generate_method_args["custom"][
                "condition"
            ]

    def visualize(self):

        z = np.random.randn(
            self.num_samples, self.input_latent_vector_size, 1, 1
        ).astype(np.float32)
        if self.conditional:
            gen_images = self.gen_function(
                condition=self.condition, input_latent_vector=z
            )
        else:
            gen_images = self.gen_function(input_latent_vector=z)
        if type(gen_images[0]) is tuple:
            image = gen_images[0][0].squeeze()
        else:
            image = gen_images[0].squeeze()

        fig, ax = plt.subplots()
        fig.suptitle(
            "Model " + self.model_id,
            fontsize=15,
            # fontweight="bold",
        )
        ax.axis("off")
        ax.set_title("Generated image")
        display = ax.imshow(image, cmap="gray", vmin=0, vmax=255)
        # adjust the main plot to make room for the sliders
        plt.subplots_adjust(left=0.45, bottom=0.2)

        padding = 0.03
        sliders_x = 0.1
        sliders_y = 0.80
        sliders_width = 0.25
        sliders_height = 0.02
        sliders = []

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
            condition_ax.set_title("Input condition: " + gen_images[0][1])

        offset_ax = plt.axes(
            (sliders_x, sliders_y - 5 * padding, sliders_width, sliders_height)
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
        # for i in range(int(self.input_latent_vector_size)):
        for i in range(int(self.input_latent_vector_size / 10)):
            axfreq = plt.axes(
                (
                    sliders_x,
                    sliders_y - (i + 7) * padding,
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

        # The function to be called anytime a slider's value changes
        def update(val):
            for i, slider in enumerate(sliders):
                for j in range(10):
                    z[0][i + j] = slider.val

            if self.conditional:
                self.condition = condition_slider.val
                gen_images = self.gen_function(
                    condition=self.condition, input_latent_vector=z
                )
                condition_ax.set_title("Input condition: " + gen_images[0][1])
            else:
                gen_images = self.gen_function(input_latent_vector=z)

            if type(gen_images[0]) is tuple:
                image = gen_images[0][0].squeeze()
            else:
                image = gen_images[0].squeeze()
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
        resetax = plt.axes([0.77, 0.155, 0.1, 0.04])
        reset_button = Button(resetax, "Reset", hovercolor="0.975")
        seedax = plt.axes([0.62, 0.155, 0.1, 0.04])
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
        plt.show()
