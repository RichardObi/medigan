import torch
import torch.utils.data
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider

from medigan import Generators

device = torch.device("cuda") if torch.cuda.is_available() else "cpu"

num_samples = 1
image_size = 128
nz = 100

# model_id = "00001_DCGAN_MMG_CALC_ROI"
model_id = "00002_DCGAN_MMG_MASS_ROI"
# model_id = "00003_CYCLEGAN_MMG_DENSITY_FULL"
model = model_id

generators = Generators()
model_executor = generators.get_model_executor(model_id)
nz = model_executor.generate_method_z_size
gen_function = generators.get_generate_function(
    model_id=model_id, num_samples=num_samples, save_images=False
)

z = torch.randn(num_samples, nz, 1, 1, device=device)
gen_images = gen_function(z=z)
image = gen_images[0].squeeze()

fig, ax = plt.subplots()
fig.suptitle(
    "Model " + model,
    fontsize=15,
    # fontweight="bold",
)
ax.axis("off")
ax.set_title("Generated image")
display = ax.imshow(image, cmap="gray", vmin=0, vmax=255)
# adjust the main plot to make room for the sliders
plt.subplots_adjust(left=0.45, bottom=0.2)

padding = 0.03
sliders = []

axfreq = plt.axes((0.1, 0.80, 0.25, 0.02))
axfreq.set_title("Input vector")
offset_slider = Slider(
    axfreq, "offset", -6, 6, valinit=0.0, initcolor="none", valfmt="%.2f"
)
sliders.append(offset_slider)
# for i in range(int(nz)):
for i in range(int(nz / 10)):
    axfreq = plt.axes((0.1, 0.80 - (i + 2) * padding, 0.25, 0.02))
    slider = Slider(
        axfreq,
        "z{}".format(i + 1),
        -3,
        3,
        valinit=float(z[0][i]),
        initcolor="none",
        valfmt="%.2f",
    )
    sliders.append(slider)


# The function to be called anytime a slider's value changes
def update(val):
    for i, slider in enumerate(sliders):
        if sliders.index(slider) == 0:
            pass
        else:
            for j in range(10):
                z[0][i + j] = slider.val + sliders[0].val

    gen_images = gen_function(z=z)
    image = gen_images[0].squeeze()
    display.set_data(image)
    fig.canvas.draw_idle()


# register the update function with each slider
for slider in sliders:
    slider.on_changed(update)

# Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
resetax = plt.axes([0.77, 0.155, 0.1, 0.04])
reset_button = Button(resetax, "Reset", hovercolor="0.975")
seedax = plt.axes([0.62, 0.155, 0.1, 0.04])
seed_button = Button(seedax, "Seed", hovercolor="0.975")


def reset(event):
    for slider in sliders:
        slider.reset()


def new_seed(event):
    z = torch.randn(num_samples, nz, 1, 1, device=device)
    for slider in sliders:
        if sliders.index(slider) == 0:
            pass
        else:
            slider.valinit = float(z[0][sliders.index(slider)])
    reset(event)


reset_button.on_clicked(reset)
seed_button.on_clicked(new_seed)
update(0)
plt.show()
