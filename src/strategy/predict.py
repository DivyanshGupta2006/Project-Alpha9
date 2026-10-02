import torch

from market.events import SignalEvent
from market.schemas import AbstractStrategy

class Strategy(AbstractStrategy):
    def __init__(self,
                 model,
                 data_handler,
                 symbols,
                 cols,
                 seq_len,
                 device):
        self.model = model.to(device)
        self.data_handler = data_handler
        self.symbols = symbols
        self.cols = cols
        self.seq_len = seq_len
        self.device = device

    def _normalize(self, raw_state):
        mean = raw_state.mean(dim=1, keepdim=True)
        std = raw_state.std(dim=1, keepdim=True)

        return (raw_state - mean) / std

    def _sanitize(self, fiducia):
        total = fiducia.abs().sum()
        return fiducia / total if total > 0 else fiducia

    #TODO: Uniformize theese three interfaces!

    @torch.no_grad()
    def action(self, raw_state, deterministic=False):
        self.model.eval()
        state = self._normalize(raw_state.to(self.device))
        dist, value = self.model(state)
        action = dist.mean if deterministic else dist.sample()
        log_prob = dist.log_prob(action).sum(dim=-1)
        return action, log_prob, value.squeeze(-1)

    def evaluate(self, raw_state, actions):
        self.model.train()
        state = self._normalize(raw_state.to(self.device))
        dist, value = self.model(state)
        log_prob = dist.log_prob(actions).sum(dim=-1)
        entropy = dist.entropy().sum(dim=-1)
        return log_prob, entropy, value.squeeze(-1)

    @torch.no_grad()
    def calculate_fiducia(self, event):
        self.model.eval()
        candles = self.data_handler.get_latest_candles(self.seq_len)
        if len(candles) < self.seq_len:
            return None

        selected_cols = [col for col in candles.columns if col[0].lower() in self.cols]
        candles = candles[selected_cols]

        raw_state = torch.tensor(
            candles.values, dtype=torch.float32, device=self.device
        ).reshape(1, self.seq_len, -1)

        state = self._normalize(raw_state)
        dist, _ = self.model(state)

        fiducia = self._sanitize(dist.mean.reshape(-1))
        fiducia_dict = dict(zip(self.symbols, fiducia.tolist()))

        return SignalEvent(event.timestamp,     fiducia_dict)