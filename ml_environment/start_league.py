import subprocess
import os
import time
import sys

def start_process(command, env=None):
    if env:
        new_env = os.environ.copy()
        new_env.update(env)
    else:
        new_env = os.environ
        
    print(f"Starting: {command}")
    return subprocess.Popen(
        command,
        shell=True,
        cwd=os.path.join(os.getcwd()),
        env=new_env,
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )

def main():
    # Set patch version
    patch = "season_03"
    print(f"--- NEON GRIDIRON: HYPER LEAGUE LAUNCHER ({patch}) ---")
    
    # 1. Kill potentially hanging processes
    subprocess.run("taskkill /F /IM python.exe", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    time.sleep(1)
    
    # 2. Start PBT League
    pbt_cmd = f".\\venv\\Scripts\\python.exe pbt_league.py"
    pbt_proc = start_process(pbt_cmd, env={"NEON_PATCH": patch})
    
    # 3. Start Telemetry Stream (Test Env)
    test_cmd = f".\\venv\\Scripts\\python.exe test_env.py"
    test_proc = start_process(test_cmd, env={"NEON_PATCH": patch})
    
    print("\nProcesses launched in separate consoles.")
    print("Monitor the consoles for logs. Press Ctrl+C in this window to terminate (not recommended).")
    
    try:
        while True:
            time.sleep(5)
            if pbt_proc.poll() is not None:
                print("WARNING: PBT League process terminated. Relaunching...")
                pbt_proc = start_process(pbt_cmd, env={"NEON_PATCH": patch})
            if test_proc.poll() is not None:
                print("WARNING: Test Env process terminated. Relaunching...")
                test_proc = start_process(test_cmd, env={"NEON_PATCH": patch})
    except KeyboardInterrupt:
        print("\nTermination requested. Use taskmgr to kill processes if consoles remain.")
        pbt_proc.terminate()
        test_proc.terminate()

if __name__ == "__main__":
    main()
