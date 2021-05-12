import torch.nn as nn


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
