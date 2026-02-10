#!/usr/bin/env python3
import argparse
import subprocess
import time
import os
import signal
import sys

def main():
    parser = argparse.ArgumentParser(description="Run simulation and analysis.")
    parser.add_argument("--duration", type=float, default=15.0, help="Simulation duration in seconds")
    # We assume the code is already compiled or we can run gradlew
    args = parser.parse_args()

    print(f"Starting simulation for {args.duration} seconds...")
    
    # 1. Run simulation in background
    # Using setsid to create a new process group so we can kill it and children easily
    sim_process = subprocess.Popen(
        ["./gradlew", "simulateJava"], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    print(f"Sim PID: {sim_process.pid}")
    
    try:
        # 2. Wait for duration
        time.sleep(args.duration)
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        # 3. Kill simulation
        print("Stopping simulation...")
        os.killpg(os.getpgid(sim_process.pid), signal.SIGTERM)
        # sim_process.terminate() could leave children running
        try:
            sim_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(sim_process.pid), signal.SIGKILL)
    
    print("Simulation finished.")
    
    # 4. Run analysis on latest log
    # We assume the log tool is in agent/tools/log_tool.py
    print("Running analysis on latest log...")
    subprocess.run([sys.executable, "agent/tools/log_tool.py", "--mode", "timestamps"])

if __name__ == "__main__":
    main()