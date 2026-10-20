from typing import Optional
import numpy as np
import gymnasium as gym
from market.events import EventQueue, MarketEvent, SignalEvent
from triton.language import dtype

from notebooks.backtest import data_handler

from notebooks.environment import max_episode_steps
from strategy.position import portfolio


class MarketEnv(gym.Env):

    def __init__(self, data_handler, portfolio, max_episode_steps, exchange=0):
        self.max_episode_steps = max_episode_steps
        self.step = 0
        self._initial_portfolio_value = portfolio.get_current_equity()
        self._current_portfolio_value = portfolio.get_current_equity()
        self._data_handler = data_handler
        self._portfolio = portfolio
        self.exchange = exchange

        self.observation_space = gym.spaces.Box(
            low = 0,
            high = 1000000000,
            shape = (77,),
            dtype = np.float32,
        )
        self.action_space = gym.spaces.Box(low = -1*1000000000, high = 1000000000, dtype = np.float32)

        
    def __get_info(self):
        candle = data_handler.get_latest_candle()
        # info = "Executed step successfully" if not truncated or not terminated else "Failed"
        info = {'equity': self._current_portfolio_value,
                'candle': candle
                }
        return info

    def step(self, action, _timestamp):
        self.step += 1
        previous_portfolio_value = self._current_portfolio_value

        fiducia_dict = dict(zip(self.symbols, action.tolist()))

        sig_event = SignalEvent(_timestamp, fiducia_dict)

        event_queue = EventQueue()
        event_queue.put_event(sig_event)

        terminated = False
        truncated = False
        while not event_queue.empty():
            event = event_queue.get_event()

            if event.type == 'SIGNAL':
                order_event = portfolio.update_signal(event)
                if order_event:
                    event_queue.put_event(order_event)

            elif event.type == 'ORDER':
                fill_event = self.exchange.execute_order(event)
                if fill_event:
                    event_queue.put_event(fill_event)

            elif event.type == 'FILL':
                self._portfolio.update_fill(event)

        if self._portfolio.is_bankrupt():
            terminated = True
        if self.step > max_episode_steps:
            truncated = True

        self._current_portfolio_value = self._portfolio.get_current_equity()
        reward = np.log(self._current_portfolio_value - previous_portfolio_value) - np.log(previous_portfolio_value)

        info = self.__get_info()

        observation = data_handler

        return observation, reward, terminated, truncated, info

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):

        super().reset(seed=seed)


        self.timestep = 0
        self._current_portfolio_value = self._initial_portfolio_value
        return
