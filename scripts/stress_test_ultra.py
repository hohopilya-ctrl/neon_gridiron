import torch
import time
from ai.env.ultra_vec_env import UltraVectorizedEnv

def run_stress_test(num_envs=4096, num_steps=500, device="cuda"):
    print(f"🔥 ULTRA GLOBAL STRESS TEST")
    print(f"Targeting 1,000,000 Steps/Sec Milestone")
    print(f"Configuration: {num_envs} envs, {num_steps} steps, device={device}")
    print(f"--------------------------------------")
    
    env = UltraVectorizedEnv(num_envs=num_envs, device=device)
    env.reset()
    
    actions = (torch.rand((num_envs, 14, 2), device=env.phys.device) * 2 - 1)
    
    # Warmup
    for _ in range(20):
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
    
    print(f"Match results [First 5 Envs]:")
    print(env.phys.pos[:5, 0, :]) # Ball pos of first 5 envs
    
    print(f"--------------------------------------")
    print(f"Execution Time: {duration:.4f} seconds")
    print(f"Total Steps: {total_steps:,}")
    print(f"FINAL THROUGHPUT: {sps:,.0f} STEPS/SEC")
    
    if sps >= 1000000:
        print(f"✅ 1M MILESTONE ACHIEVED")
    else:
        print(f"⚠️ Milestone missed (Currently at {sps:,.0f} SPS)")
    print(f"--------------------------------------")

if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Note: On CPU, 4096 envs might be heavy, but we verify the logic
    run_stress_test(num_envs=2048, num_steps=200, device=device)
