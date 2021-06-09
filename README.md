A sample python package deployment for MediGan ToolBox.


import medigan as datasets

dataset = datasets.DCGAN(root="dataset/", transform=transforms, download=True)
loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)