import torch

class Model:
    def __init__(self, symbols, model_dir):
        self.symbols = symbols
        self.model_dir = model_dir

    def forward(self, x):
        return torch.tensor([0.2, 0.2, 0.2, 0.2, 0.2])

    def save(self):
        pass

    def load(self):
        pass