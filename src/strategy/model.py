import torch
import torch.nn as nn
from torch.distributions import Normal

class Model(nn.Module):
    def __init__(self,
                 obs_dim,
                 action_dim,
                 lstm_hidden_dim=128,
                 num_lstm_layers=2,
                 mlp_hidden_dim=128,
                 log_std_init=0.0,
                 model_dir=None
                 ):
        super().__init__()

        self.model_dir = model_dir

        self.pre_lstm = nn.Sequential(
            nn.Linear(obs_dim, mlp_hidden_dim),
            nn.Tanh()
        )

        self.lstm = nn.LSTM(
            input_size=mlp_hidden_dim,
            hidden_size=lstm_hidden_dim,
            num_layers=num_lstm_layers,
            batch_first=True,
        )

        self.actor_mean = nn.Sequential(
            nn.Linear(lstm_hidden_dim, mlp_hidden_dim),
            nn.Tanh(),
            nn.Linear(mlp_hidden_dim, action_dim)
        )
        self.actor_log_std = nn.Parameter(torch.ones(action_dim) * log_std_init)

        self.critic = nn.Sequential(
            nn.Linear(lstm_hidden_dim, mlp_hidden_dim),
            nn.Tanh(),
            nn.Linear(mlp_hidden_dim, 1)
        )

        self._init_weights()

    def _init_weights(self):
        for module in [self.pre_lstm, self.critic]:
            for layer in module:
                if isinstance(layer, nn.Linear):
                    nn.init.orthogonal_(layer.weight)
                    nn.init.constant_(layer.bias, 0)

        for layer in self.actor_mean:
            if isinstance(layer, nn.Linear):
                nn.init.orthogonal_(layer.weight, gain=0.01)
                nn.init.constant_(layer.bias, 0)

    def forward(self, state):
        x = self.pre_lstm(state)
        lstm_out, _ = self.lstm(x)
        lstm_out = lstm_out[:, -1, :]

        mean = self.actor_mean(lstm_out)
        std = torch.exp(self.actor_log_std).expand_as(mean)
        dist = Normal(mean, std)

        value = self.critic(lstm_out)

        return dist, value

    def save(self):
        torch.save(self.state_dict(), self.model_dir)

    def load(self, device, set_eval=True):
        checkpoint = torch.load(self.model_dir, map_location=device)
        self.load_state_dict(checkpoint)
        self.to(device)
        if set_eval:
            self.eval()