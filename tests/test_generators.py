from medigan import Generators


def test_generate():
    generators = Generators()

    # images = generators.generate(model_id="00001_DCGAN_MMG_CALC_ROI", num_samples=10, save_images=False)
    images = generators.generate(model_id="00001_DCGAN_MMG_CALC_ROI", num_samples=10)

    assert len(images) == 10

