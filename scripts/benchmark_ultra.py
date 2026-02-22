import time
import numpy as np
from ai.env.neon_env import NeonFootballEnv

def run_benchmark(steps: int = 1000):
    print(f"Starting ULTRA Benchmark ({steps} steps)...")
    env = NeonFootballEnv({"team_size": 7})
    env.reset()
    
    start_time = time.time()
    for _ in range(steps):
        action = env.action_space.sample()
        env.step(action)
    end_time = time.time()
    
    total_time = end_time - start_time
    sps = steps / total_time
    
    print(f"Total Time: {total_time:.4f}s")
    print(f"Steps Per Second (SPS): {sps:.2f}")
    print(f"Target FPS (60): {'PASSED' if sps > 60 else 'FAILED'}")
    
    if sps < 60:
        print("WARNING: Simulation is slower than real-time!")
    else:
        print("PERFORMANCE: Simulation is running faster than real-time! ✅")

if __name__ == "__main__":
    run_benchmark()
