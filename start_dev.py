#!/usr/bin/env python3
import os
import subprocess
import sys

# Import eaia to load environment
import eaia

def main():
    # Run langgraph dev with the current environment
    process = subprocess.Popen(
        ["langgraph", "dev"],
        env=os.environ,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    main()
