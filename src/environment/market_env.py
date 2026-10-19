from typing import Optional
import numpy as np
import gymnasium as gym


class MarketEnv(gym.Env):

    def __init__(self, current_portfolio_value, data_handler, portfolio_manager, max_episode_steps=0):
        self.max_episode_steps = max_episode_steps
        self.timestep = 0
        self.current_portfolio_value = current_portfolio_value
        self.initial_portfolio_value = current_portfolio_value
        self.data_handler = data_handler
        self.portfolio_manager = portfolio_manager

    def __get_info(self):
        # for detailed logs if required.
        pass

    def step(self, action):
        self.timestep += 1
        previous_portfolio_value = self.current_portfolio_value
        self.current_portfolio_value += action  # update

        candle = self.data_handler.get_candle(self.timestep)  # assuming its a list

        self.current_portfolio_value = self.portfolio_manager.portfolio_value
        reward = np.log(self.current_portfolio_value) - np.log(previous_portfolio_value)

        observation = candle.append(self.current_portfolio_value)

        terminated = False
        truncated = False

        # check for truncation or termination
        if self.timestep > self.max_episode_steps:
            truncated = True
        if self.current_portfolio_value < 0:
            terminated = True

        info = "Executed step successfully" if not truncated or not terminated else "Failed"
        return observation, reward, terminated, truncated, info
        pass

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        self.timestep = 0
        self.current_portfolio_value = self.initial_portfolio_value
