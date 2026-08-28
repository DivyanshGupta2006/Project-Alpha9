import torch
import torch.nn as nn


class Model(nn.Module):
    def __init__(self, symbols, model_dir):
        super().__init__()
        self.symbols = symbols
        self.model_dir = model_dir

    def forward(self, x):
        return torch.tensor([-0.1, 0.4, 0.3, -0.2])

    def save(self):
        pass

    def load(self):
        pass