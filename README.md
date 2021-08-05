MediGAN is a Python library to implement Generative Adversarial Networks(GANs), Conditional GANs, Adversarial Auto-Encoders(AAEs) etc This library aims to enhance data augmentation via providing/ generating training data sets for other Deep learning models.

Dependencies
numpy:
PyTorch



import medigan as dataset


dataset.generate_dataset(model_name,number_of_samples,destination_folder)



#print (dataset.get_meta_data(model_name,performance_key))