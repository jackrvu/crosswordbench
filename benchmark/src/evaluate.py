import os
import csv
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv
import anthropic
import requests
from tqdm import tqdm
from openai import OpenAI  # new v1.x client

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
            # Instantiate the new OpenAI client; it reads OPENAI_API_KEY by default
            self.client = OpenAI()
        elif self.model_name.startswith('claude'):
            anthropic.api_key = os.getenv('ANTHROPIC_API_KEY')
            self.client = anthropic.Anthropic()
        elif self.model_name in ['deepseek-chat', 'deepseek-reasoner']:
            self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
            if not self.deepseek_api_key:
                raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        else:
            raise ValueError(f"Unsupported model: {self.model_name}")
    
    def _generate_prompt(self, clues: List[Dict]) -> str:
        prompt = "You are solving a crossword puzzle. Given the clues and their answer lengths, provide the correct words.\n\n"
        for i, clue in enumerate(clues, 1):
            prompt += f"{i}. Clue: {clue['Clue']}\n   Length: {clue['Length']}\n\n"
        prompt += (
            "Please provide your answers as a JSON array of strings, in the same order as the clues. "
            "Only provide the answer words, with no additional explanation or punctuation."
        )
        return prompt

    def _get_model_response(self, prompt: str) -> List[str]:
        if self.model_name.startswith('gpt'):
            # new v1.x interface
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=1000
            )
            # content is now response.choices[0].message.content
            content = response.choices[0].message.content.strip()
            # strip markdown fences if any
            content = content.replace('```json', '').replace('```', '').strip()
            # if it's a pure JSON array, parse directly
            if content.startswith('[') and content.endswith(']'):
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    pass
            # otherwise, try to massage into a JSON list
            try:
                # remove outer brackets if double-bracketed
                inner = content
                if inner.startswith('[') and inner.endswith(']'):
                    inner = inner[1:-1].strip()
                return json.loads(f"[{inner}]")
            except json.JSONDecodeError:
                # fallback: split by lines
                return [line.strip().strip('"\'.,') for line in content.splitlines() if line.strip()]

        elif self.model_name.startswith('claude'):
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=1000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text.strip()
            content = content.replace('```json', '').replace('```', '').strip()
            if content.startswith('[') and content.endswith(']'):
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    pass
            try:
                inner = content
                if inner.startswith('[') and inner.endswith(']'):
                    inner = inner[1:-1].strip()
                return json.loads(f"[{inner}]")
            except json.JSONDecodeError:
                return [line.strip().strip('"\'.,') for line in content.splitlines() if line.strip()]

        elif self.model_name in ['deepseek-chat', 'deepseek-reasoner']:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 10000
            }
            resp = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            resp.raise_for_status()
            response_data = resp.json()
            print("\nRaw Deepseek API Response:")
            print(json.dumps(response_data, indent=2))
            content = response_data['choices'][0]['message']['content'].strip()
            content = content.replace('```json', '').replace('```', '').strip()
            if content.startswith('[') and content.endswith(']'):
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    pass
            try:
                inner = content
                if inner.startswith('[') and inner.endswith(']'):
                    inner = inner[1:-1].strip()
                return json.loads(f"[{inner}]")
            except json.JSONDecodeError:
                return [line.strip().strip('"\'.,') for line in content.splitlines() if line.strip()]

    def evaluate(self, dataset_path: str, output_path: str, batch_size: int = 50):
        results = []
        correct = 0
        total = 0
        
        with open(dataset_path, 'r', encoding='latin-1') as f:
            reader = csv.DictReader(f)
            all_rows = list(reader)[:5000]  # limit to 5k
        
        for i in tqdm(range(0, len(all_rows), batch_size), desc=f"Evaluating {self.model_name}"):
            batch = all_rows[i:i + batch_size]
            prompt = self._generate_prompt(batch)
            
            try:
                responses = self._get_model_response(prompt)
                # normalize length
                if len(responses) != len(batch):
                    print(f"Warning: Expected {len(batch)} responses, got {len(responses)}")
                    responses = responses[:len(batch)] + [''] * max(0, len(batch) - len(responses))
                
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
                
                time.sleep(self.config.get('rate_limit', 0.1))
            except Exception as e:
                print(f"Error processing batch: {e}")
                continue
        
        accuracy = (correct / total) * 100 if total else 0
        output_file = Path(output_path) / f"{self.model_name}_results.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
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
    model_name = os.getenv('MODEL_NAME', 'deepseek-reasoner')
    config_path = 'config/model_config.json'
    dataset_path = '../dataset/nytcrosswords.csv'
    output_path = 'results'
    
    evaluator = ModelEvaluator(model_name, config_path)
    evaluator.evaluate(dataset_path, output_path, batch_size=50)

if __name__ == "__main__":
    main()
