import time

import torch

from ai.env.ultra_vec_env import UltraVectorizedEnv


def run_benchmark(num_envs=1024, num_steps=1000, device="cuda"):
    print(f"🚀 ULTRA Benchmark: {num_envs} envs, {num_steps} steps, device={device}")
    
    env = UltraVectorizedEnv(num_envs=num_envs, device=device)
    env.reset()
    
    # Generate random actions on the same device
    # action_space shape is (num_envs, 14, 2)
    actions = (torch.rand((num_envs, 14, 2), device=env.phys.device) * 2 - 1)
    
    # Warmup
    for _ in range(10):
        env.step(actions)
        
    torch.cuda.synchronize() if device == "cuda" else None
    start_time = time.time()
    
    total_steps = 0
    for _ in range(num_steps):
        env.step(actions)
        total_steps += num_envs
        
    torch.cuda.synchronize() if device == "cuda" else None
    end_time = time.time()
    
    duration = end_time - start_time
    sps = total_steps / duration
    
    print("--------------------------------------")
    print(f"Execution Time: {duration:.2f} seconds")
    print(f"Total Steps: {total_steps}")
    print(f"Throughput: {sps:,.0f} STEPS/SEC")
    print("--------------------------------------")

if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    run_benchmark(num_envs=1024, num_steps=1000, device=device)
