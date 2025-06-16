import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

def load_results(results_dir: str) -> Dict[str, Dict]:
    """Load all result files from the results directory."""
    results = {}
    for file in Path(results_dir).glob("*_results.json"):
        model_name = file.stem.replace("_results", "")
        with open(file, 'r') as f:
            results[model_name] = json.load(f)
    return results

def get_model_provider(model_name: str) -> str:
    """Get the provider name for a model."""
    if model_name.startswith('gpt'):
        return 'OpenAI'
    elif model_name.startswith('claude'):
        return 'Anthropic'
    elif model_name.startswith('deepseek'):
        return 'DeepSeek'
    return 'Unknown'

def generate_html(results: Dict[str, Dict]) -> str:
    """Generate HTML content for the results page."""
    # Start with the template HTML
    with open('results/index.html', 'r') as f:
        template = f.read()
    
    # Group models by provider
    providers = {
        'OpenAI': [],
        'Anthropic': [],
        'DeepSeek': []
    }
    
    for model_name, data in results.items():
        provider = get_model_provider(model_name)
        if provider in providers:
            providers[provider].append((model_name, data))
    
    # Replace model cards for each provider
    for provider, models in providers.items():
        if not models:
            continue
            
        # Find the provider's model group section
        start_marker = f'<h2 class="model-group-title">{provider} Models</h2>'
        end_marker = '</div>\n    </div>'
        
        # Generate new content for this provider's section
        new_content = f'<h2 class="model-group-title">{provider} Models</h2>\n        <div class="results-container">'
        
        for model_name, data in models:
            model_card = f"""
            <div class="model-card">
                <div class="model-name">{model_name}</div>
                <div class="model-provider">{provider}</div>
                <div class="accuracy">{data['accuracy']:.2f}%</div>
                <div class="stats">
                    <p>Total Questions: {data['total_questions']}</p>
                    <p>Correct Answers: {data['correct_answers']}</p>
                    <p>Average Response Time: --</p>
                </div>
            </div>
            """
            new_content += model_card
        
        new_content += '\n        </div>\n    </div>'
        
        # Replace the section in the template
        start_idx = template.find(start_marker)
        if start_idx != -1:
            end_idx = template.find(end_marker, start_idx) + len(end_marker)
            template = template[:start_idx] + new_content + template[end_idx:]
    
    # Update timestamp
    template = template.replace('Not yet run', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Remove disclaimer if results exist
    if results:
        template = template.replace(
            '<div class="disclaimer">\n        <strong>Note:</strong> This is a template results page. The actual benchmark results have not been populated yet. The data shown below is placeholder information.\n    </div>',
            ''
        )
    
    return template

def main():
    results_dir = 'results'
    results = load_results(results_dir)
    
    if not results:
        print("No results found. Using template page.")
        return
    
    html_content = generate_html(results)
    
    # Save the updated page
    with open('results/index.html', 'w') as f:
        f.write(html_content)
    
    print("Results page generated successfully!")

if __name__ == "__main__":
    main() 