import os
import subprocess
from typing import List
from dotenv import load_dotenv

def run_benchmark(model_name: str):
    """Run the benchmark for a specific model."""
    print(f"\nRunning benchmark for {model_name}...")
    
    # Update the MODEL_NAME in .env
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    with open('.env', 'w') as f:
        for line in lines:
            if line.startswith('MODEL_NAME='):
                f.write(f'MODEL_NAME={model_name}\n')
            else:
                f.write(line)
    
    # Run the evaluation script
    subprocess.run(['python', 'src/evaluate.py'])

def main():
    # List of models to evaluate
    models = [
        'gpt-4',
        'gpt-3.5-turbo',
        'claude-3-opus',
        'claude-3-sonnet'
    ]
    
    # Run benchmarks for each model
    for model in models:
        run_benchmark(model)

if __name__ == "__main__":
    main() 