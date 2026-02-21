import os
import random
import json
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import VecEnv
import shutil

from env.football_env import NeonGridironEnv

class CompetitiveSelfPlayVecEnv(VecEnv):
    def __init__(self, opponent_model_path=None, learning_team=0):
        self.env = NeonGridironEnv()
        self.num_agents = self.env.cfg['match']['max_players_per_team']
        self.learning_team = learning_team
        
        self.opponent_model = None
        if opponent_model_path and os.path.exists(opponent_model_path):
            self.opponent_model = PPO.load(opponent_model_path)
            
        super().__init__(self.num_agents, self.env.observation_space["agent_0"], self.env.action_space["agent_0"])
        self.last_obs = None
        
    def _get_learning_indices(self):
        n = self.num_agents
        return range(0, n) if self.learning_team == 0 else range(n, n*2)
        
    def _get_opponent_indices(self):
        n = self.num_agents
        return range(n, n*2) if self.learning_team == 0 else range(0, n)

    def reset(self):
        obs_dict, _ = self.env.reset()
        self.last_obs = obs_dict
        return np.array([obs_dict[f"agent_{i}"] for i in self._get_learning_indices()])

    def step_async(self, actions):
        self.learning_actions = actions

    def step_wait(self):
        action_dict = {}
        learning_idx = list(self._get_learning_indices())
        opp_idx = list(self._get_opponent_indices())
        
        # Populate learning team actions
        for i, global_i in enumerate(learning_idx):
            action_dict[f"agent_{global_i}"] = self.learning_actions[i]
            
        # Predict opponent actions
        if self.opponent_model is not None:
            opp_obs_array = np.array([self.last_obs[f"agent_{i}"] for i in opp_idx])
            # Added basic noise for exploration in self-play
            opp_actions, _ = self.opponent_model.predict(opp_obs_array, deterministic=False)
            for i, global_i in enumerate(opp_idx):
                action_dict[f"agent_{global_i}"] = opp_actions[i]
        else:
            # Random actions if no opponent model
            for global_i in opp_idx:
                action_dict[f"agent_{global_i}"] = self.env.action_space[f"agent_{global_i}"].sample()
                
        # Step environment
        obs_dict, rewards_dict, term_dict, trunc_dict, infos_dict = self.env.step(action_dict)
        self.last_obs = obs_dict
        
        # Extract for SB3
        obs_array = np.array([obs_dict[f"agent_{i}"] for i in learning_idx])
        rewards_array = np.array([rewards_dict[f"agent_{i}"] for i in learning_idx])
        dones_array = np.array([term_dict[f"agent_{i}"] or trunc_dict[f"agent_{i}"] for i in learning_idx])
        
        # Check if match ended
        if any(dones_array):
            last_info = infos_dict["agent_0"]
            self.last_goal_team = last_info.get("goal_team", -1)
            
            obs_dict, _ = self.env.reset()
            self.last_obs = obs_dict
            obs_array = np.array([obs_dict[f"agent_{i}"] for i in learning_idx])
            
        infos = [{}] * self.num_agents
        return obs_array, rewards_array, dones_array, infos

    def close(self):
        self.env.close()

    def get_attr(self, attr_name, indices=None):
        return [getattr(self, attr_name, None) for _ in range(self.num_agents)]
    def set_attr(self, attr_name, value, indices=None): pass
    def env_method(self, method_name, *method_args, indices=None, **method_kwargs): pass
    def env_is_wrapped(self, wrapper_class, indices=None): return [False]*self.num_agents
    def render(self, mode="human"): return self.env.render(mode)


def setup_population(num_models=4, base_model_path=None):
    os.makedirs("models/pbt", exist_ok=True)
    population = []
    
    # Check if existing PBT models are already there, and find the highest generation
    import glob
    existing_models = glob.glob("models/pbt/gen_*_model_*.zip")
    
    highest_gen = 0
    if existing_models:
        for f in existing_models:
            try:
                gen_num = int(f.split("gen_")[1].split("_")[0])
                if gen_num > highest_gen:
                    highest_gen = gen_num
            except: pass
            
    for i in range(num_models):
        target_name = f"gen_{highest_gen}_model_{i}"
        target_path = f"models/pbt/{target_name}.zip"
        
        env = CompetitiveSelfPlayVecEnv(learning_team=0)
        
        # If we found pre-existing PBT model, load it
        if os.path.exists(target_path):
            model = PPO.load(target_path, env=env)
            model_name = target_name
            model_path = target_path
            print(f"Resuming existing model: {model_name}")
        else:
            model_name = f"gen_0_model_{i}"
            model_path = f"models/pbt/{model_name}.zip"
            if base_model_path and os.path.exists(base_model_path):
                model = PPO.load(base_model_path, env=env)
            else:
                policy_kwargs = dict(net_arch=dict(pi=[512, 512, 256], qf=[512, 512, 256], vf=[512, 512, 256]))
                model = PPO("MlpPolicy", env, verbose=0, n_steps=2048, policy_kwargs=policy_kwargs)
                
            # Mutate Hyperparameters (Learning Rate)
            lr_multiplier = random.uniform(0.7, 1.3)
            model.learning_rate = 0.0003 * lr_multiplier
            model.save(model_path)
            
        population.append({
            "name": model_name,
            "path": model_path,
            "elo": 1200,
            "lr": model.learning_rate
        })
        
    return population, highest_gen

def calculate_elo(rating_a, rating_b, score_a, score_b, k=32):
    # score is 1 for win, 0 for loss, 0.5 for draw
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    expected_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))
    
    new_a = rating_a + k * (score_a - expected_a)
    new_b = rating_b + k * (score_b - expected_b)
    return new_a, new_b

def play_match(model_a_info, model_b_info, timesteps=30000):
    print(f"\n--- MATCH: {model_a_info['name']} vs {model_b_info['name']} ---")
    
    # Train Model A against Model B
    print(f"Training {model_a_info['name']} against {model_b_info['name']} for {timesteps} steps...")
    env_a = CompetitiveSelfPlayVecEnv(opponent_model_path=model_b_info['path'], learning_team=0)
    model_a = PPO.load(model_a_info['path'], env=env_a)
    model_a.learn(total_timesteps=timesteps)
    model_a.save(model_a_info['path'])
    
    # Evaluate
    print(f"Evaluating {model_a_info['name']} vs {model_b_info['name']}...")
    env_eval = CompetitiveSelfPlayVecEnv(opponent_model_path=model_b_info['path'], learning_team=0)
    model_eval = PPO.load(model_a_info['path'], env=env_eval)
    obs = env_eval.reset()
    
    a_score = 0
    b_score = 0
    
    episodes = 0
    while episodes < 5:
        actions, _ = model_eval.predict(obs, deterministic=True)
        obs, rewards, dones, infos = env_eval.step(actions)
        if any(dones):
            goal_team = getattr(env_eval, 'last_goal_team', -1)
            if goal_team == 0:
                a_score += 1
            elif goal_team == 1:
                b_score += 1
            episodes += 1
            obs = env_eval.reset()
            
    # Calculate Elo
    if a_score > b_score:
        result_a, result_b = 1.0, 0.0
        print(f"Winner: {model_a_info['name']} ({a_score} - {b_score})")
    elif b_score > a_score:
        result_a, result_b = 0.0, 1.0
        print(f"Winner: {model_b_info['name']} ({b_score} - {a_score})")
    else:
        result_a, result_b = 0.5, 0.5
        print(f"Draw! ({a_score} - {b_score})")
        
    model_a_info['elo'], model_b_info['elo'] = calculate_elo(
        model_a_info['elo'], model_b_info['elo'], result_a, result_b
    )


def run_pbt_generation(population, generation):
    print(f"\n================ GENERATION {generation} ================")
    
    # Elo-based Matchmaking (Phase 16)
    # Sort by Elo and pair adjacent skilled models to ensure productive training
    population.sort(key=lambda x: x['elo'], reverse=True)
    pairs = [(0, 1), (2, 3)] 
    
    for p1, p2 in pairs:
        play_match(population[p1], population[p2], timesteps=50000)
        
    # Sort population by Elo
    population.sort(key=lambda x: x['elo'], reverse=True)
    
    print("\n--- LEADERBOARD ---")
    for idx, member in enumerate(population):
        print(f"{idx+1}. {member['name']} | Elo: {member['elo']:.1f} | LR: {member['lr']:.6f}")
        
    # Exploit and Explore (PBT)
    print("\nExecuting PBT Exploit & Explore (Phase 16: Elite Inheritance)...")
    top_model = population[0]
    bottom_model = population[-1]
    
    print(f"Propagating traits from {top_model['name']} to {bottom_model['name']}...")
    # Elite Inheritance: Load top model, but slightly mutate weights or keep current if performing well
    # For now, we do a full copy but keep the LR mutation aggressive
    shutil.copyfile(top_model['path'], bottom_model['path'])
    
    # Mutate hyperparams
    mutator = random.choice([0.8, 1.2]) 
    bottom_model['lr'] = top_model['lr'] * mutator
    print(f"Inherited & Mutated LR for {bottom_model['name']}: {bottom_model['lr']:.6f}")
    
    # Update names for next generation
    for i in range(len(population)):
        new_name = f"gen_{generation}_model_{i}"
        new_path = f"models/pbt/{new_name}.zip"
        os.rename(population[i]['path'], new_path)
        population[i]['name'] = new_name
        population[i]['path'] = new_path
        
    # Save History (Phase 17.4)
    history_file = "models/pbt/history.json"
    history = []
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
            
    history.append({
        "gen": generation,
        "avg_elo": float(np.mean([m['elo'] for m in population])),
        "max_elo": float(max([m['elo'] for m in population])),
        "timestamp": time.time()
    })
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=4)
        
    return population

if __name__ == "__main__":
    baseline = None # New Observation space means old models cannot be loaded
    print("Initialize Population from Baseline:", baseline)
    pop, start_gen = setup_population(num_models=4, base_model_path=baseline)
    
    best_all_time_elo = 0
    gen = start_gen + 1
    
    try:
        while True:
            pop = run_pbt_generation(pop, gen)
            
            # Save the current best model explicitly
            current_best = pop[0] # List is sorted by Elo in run_pbt_generation
            if current_best['elo'] > best_all_time_elo:
                best_all_time_elo = current_best['elo']
                shutil.copyfile(current_best['path'], "models/best_neon_gridiron_ppo.zip")
                print(f"\n[!] New All-Time Best Model Saved! (Elo: {best_all_time_elo:.1f}) -> models/best_neon_gridiron_ppo.zip")
                
            gen += 1
            
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user. Saving current population...")
        print(f"To resume or test, use the 'models/best_neon_gridiron_ppo.zip' file!")
