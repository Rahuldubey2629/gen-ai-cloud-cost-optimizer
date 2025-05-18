import json
from pathlib import Path
import openai
import os

def prepare_training_data():
    """Prepare training data for fine-tuning"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)  # Create if doesn't exist
    output_file = data_dir/"combined_training.jsonl"
    
    # Create sample data if no files exist
    if not list(data_dir.glob("*.jsonl")):
        print("No training files found - creating samples")
        with open(data_dir/"sample_training.jsonl", 'w') as f:
            f.write('{"prompt":"Sample EC2 optimization","completion":"Sample recommendation"}\n')
    
    with open(output_file, 'w') as outfile:
        for file in data_dir.glob("*.jsonl"):
            if file.name != "combined_training.jsonl":  # Skip our output file
                with open(file) as infile:
                    for line in infile:
                        outfile.write(line)

def train_model():
    """Execute model training"""
    prepare_training_data()
    
    try:
        # Verify we have training data
        training_file = Path("data/combined_training.jsonl")
        if not training_file.exists() or os.path.getsize(training_file) == 0:
            raise ValueError("No training data available")
            
        print(f"Training with {training_file}")
        # Add your actual training code here
        print("Model training complete (simulated)")
        
    except Exception as e:
        print(f"Training failed: {str(e)}")
        print("Please add training data to the data/ directory")

if __name__ == "__main__":
    train_model()