import os
import argparse
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback

# We use the pettingzoo parallel-to-gymnasium wrapper
from supersuit import pettingzoo_env_to_vec_env_v1, concat_vec_envs_v1
from env.football_env import NeonGridironEnv

import gymnasium as gym

class FlattenedMultiAgentEnv(gym.Env):
    """
    Wraps our single NeonGridironEnv into a Vector Env equivalent for SB3.
    It takes 1 step in the real env, but returns 14 observations.
    """
from stable_baselines3.common.vec_env import VecEnv

class MultiAgentToVecEnv(VecEnv):
    """
    Acts like a vectorized environment for SB3, but under the hood
    drives a single multi-agent Gym environment.
    """
    
    def __init__(self, env):
        self.env = env
        self.num_agents = env.num_agents
        
        # SB3 BaseVecEnv signature is (num_envs, obs_space, act_space)
        super().__init__(self.num_agents, env.observation_space["agent_0"], env.action_space["agent_0"])

    def reset(self):
        obs_dict, _ = self.env.reset()
        obs_array = np.array([obs_dict[f"agent_{i}"] for i in range(self.num_agents)])
        return obs_array

    def step_async(self, actions):
        self.actions = actions

    def step_wait(self):
        action_dict = {f"agent_{i}": self.actions[i] for i in range(self.num_agents)}
        obs_dict, rewards_dict, term_dict, trunc_dict, infos_dict = self.env.step(action_dict)
        
        obs_array = np.array([obs_dict[f"agent_{i}"] for i in range(self.num_agents)])
        rewards_array = np.array([rewards_dict[f"agent_{i}"] for i in range(self.num_agents)])
        
        dones_array = np.array([term_dict[f"agent_{i}"] or trunc_dict[f"agent_{i}"] for i in range(self.num_agents)])
        
        if any(dones_array):
            obs_dict, _ = self.env.reset()
            obs_array = np.array([obs_dict[f"agent_{i}"] for i in range(self.num_agents)])
            
        infos = [{} for _ in range(self.num_agents)]
        return obs_array, rewards_array, dones_array, infos

    def close(self):
        self.env.close()

    def get_attr(self, attr_name, indices=None):
        return [getattr(self, attr_name, None) for _ in range(self.num_agents)]
        
    def set_attr(self, attr_name, value, indices=None):
        pass
        
    def env_method(self, method_name, *method_args, indices=None, **method_kwargs):
        pass
        
    def env_is_wrapped(self, wrapper_class, indices=None):
        return [False]*self.num_agents

    def render(self, mode="human"):
        return self.env.render()

def make_env():
    # Supersuit converts our custom un AEC/Parallel dict env to a standard single-agent Gym VecEnv
    def _init():
        env = NeonGridironEnv()
        return MultiAgentToVecEnv(env)
    return _init

def train():
    print("Initializing Vector Environment...")
    # Our env simulates 14 agents. We wrapped it in MultiAgentToVecEnv,
    # which tells SB3 that it is dealing with 14 parallel environments.
    # Therefore, we do NOT need SubprocVecEnv. We just pass our VecEnv directly!
    env = MultiAgentToVecEnv(NeonGridironEnv())
    
    # Checkpoint callback to save model every 50k steps
    checkpoint_callback = CheckpointCallback(
        save_freq=50000,
        save_path='./models/',
        name_prefix='neon_gridiron_ppo'
    )
    
    print("Setting up PPO Model...")
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=512,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        tensorboard_log="./ppo_neon_tensorboard/"
    )
    
    print("Starting Training! (Press Ctrl+C to stop)")
    try:
        model.learn(total_timesteps=5_000_000, callback=checkpoint_callback)
    except KeyboardInterrupt:
        print("Training interrupted manually.")
    finally:
        print("Saving final model...")
        model.save("models/neon_gridiron_ppo_final")
        env.close()

if __name__ == "__main__":
    import os
    os.makedirs("models", exist_ok=True)
    train()
