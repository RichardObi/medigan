import torch.nn as nn


class BaseDiscriminator(nn.Module):
    def __init__(
        self, ndf: int, nc: int, ngpu: int, leakiness: float = 0.2, bias: bool = False
    ):
        super(BaseDiscriminator, self).__init__()
        self.ndf = ndf
        self.nc = nc
        self.ngpu = ngpu
        self.leakiness = leakiness
        self.bias = bias
        self.main = None

    def forward(self, input):
        raise NotImplementedError
