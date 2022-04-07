import pytest
from medigan import Generators

models_list = ["00001_DCGAN_MMG_CALC_ROI", 
"00002_DCGAN_MMG_MASS_ROI",
"00003_CYCLEGAN_MMG_DENSITY_FULL"
]

@pytest.mark.parametrize("model_id", models_list)
def test_generate_model(model_id):
    generators = Generators()

    images = generators.generate(model_id=model_id, num_samples=3, save_images=False)

    assert len(images) == 3
