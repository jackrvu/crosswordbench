import os
import csv
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv
import openai
import anthropic
import requests
from tqdm import tqdm

# Load environment variables
load_dotenv()

class ModelEvaluator:
    def __init__(self, model_name: str, config_path: str):
        self.model_name = model_name
        self.config = self._load_config(config_path)
        self._setup_api_keys()
        
    def _load_config(self, config_path: str) -> Dict:
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _setup_api_keys(self):
        if self.model_name.startswith('gpt'):
            openai.api_key = os.getenv('OPENAI_API_KEY')
        elif self.model_name.startswith('claude'):
            anthropic.api_key = os.getenv('ANTHROPIC_API_KEY')
        elif self.model_name == 'deepseek-chat':
            self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
            if not self.deepseek_api_key:
                raise ValueError("DEEPSEEK_API_KEY environment variable not set")
    
    def _generate_prompt(self, clues: List[Dict]) -> str:
        prompt = "You are solving a crossword puzzle. Given the clues and their answer lengths, provide the correct words.\n\n"
        for i, clue in enumerate(clues, 1):
            prompt += f"{i}. Clue: {clue['Clue']}\n   Length: {clue['Length']}\n\n"
        prompt += "Please provide your answers as a JSON array of strings, in the same order as the clues. Only provide the answer words, with no additional explanation or punctuation."
        return prompt

    def _get_model_response(self, prompt: str) -> List[Dict[str, str]]:
        """Get response from the model and parse it as JSON."""
        try:
            if self.model_name.startswith("gpt"):
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                content = response.choices[0].message.content
            elif self.model_name.startswith("claude"):
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=4096,
                    temperature=0,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            elif self.model_name.startswith("deepseek"):
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                content = response.choices[0].message.content
            else:
                raise ValueError(f"Unsupported model: {self.model_name}")

            # Parse the response as JSON
            try:
                # Remove first two and last two responses as they are syntactical
                responses = json.loads(content)
                if len(responses) > 4:  # Only remove if we have enough responses
                    responses = responses[2:-2]
                return responses
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract answers from text
                print(f"Failed to parse JSON response from {self.model_name}")
                print("Raw response:", content)
                return self._extract_answers_from_text(content)

        except Exception as e:
            print(f"Error getting response from {self.model_name}: {str(e)}")
            return []

    def evaluate(self, dataset_path: str, output_path: str, batch_size: int = 50):
        results = []
        correct = 0
        total = 0
        
        # Read all rows from the dataset
        with open(dataset_path, 'r', encoding='latin-1') as f:
            reader = csv.DictReader(f)
            all_rows = list(reader)
        
        # Process in batches
        for i in tqdm(range(0, len(all_rows), batch_size), desc=f"Evaluating {self.model_name}"):
            batch = all_rows[i:i + batch_size]
            prompt = self._generate_prompt(batch)
            
            try:
                responses = self._get_model_response(prompt)
                
                # Ensure we have the right number of responses
                if len(responses) != len(batch):
                    print(f"Warning: Expected {len(batch)} responses, got {len(responses)}")
                    responses = responses[:len(batch)]  # Truncate if too many
                    responses.extend([''] * (len(batch) - len(responses)))  # Pad if too few
                
                # Process each response
                for clue, response in zip(batch, responses):
                    is_correct = response.lower() == clue['Word'].lower()
                    correct += int(is_correct)
                    total += 1
                    
                    results.append({
                        'clue': clue['Clue'],
                        'expected': clue['Word'],
                        'received': response,
                        'is_correct': is_correct
                    })
                
                # Rate limiting between batches
                time.sleep(self.config.get('rate_limit', 0.1))
                
            except Exception as e:
                print(f"Error processing batch: {e}")
                continue
        
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        # Save detailed results
        output_file = Path(output_path) / f"{self.model_name}_results.json"
        with open(output_file, 'w') as f:
            json.dump({
                'model': self.model_name,
                'accuracy': accuracy,
                'total_questions': total,
                'correct_answers': correct,
                'detailed_results': results
            }, f, indent=2)
        
        print(f"\nResults for {self.model_name}:")
        print(f"Accuracy: {accuracy:.2f}%")
        print(f"Total questions: {total}")
        print(f"Correct answers: {correct}")
        print(f"Detailed results saved to: {output_file}")

def main():
    # Example usage
    model_name = os.getenv('MODEL_NAME', 'deepseek-chat')
    config_path = 'config/model_config.json'
    dataset_path = '../dataset/nytcrosswords.csv'
    output_path = 'results'
    
    evaluator = ModelEvaluator(model_name, config_path)
    evaluator.evaluate(dataset_path, output_path, batch_size=50)

if __name__ == "__main__":
    main() 