# Crossword Puzzle LLM Benchmark

This benchmark evaluates the performance of Large Language Models (LLMs) on solving crossword puzzle clues. The benchmark uses the NYT Crosswords dataset and provides a standardized way to compare different models' abilities to solve crossword clues.

## Dataset

The benchmark uses the Kaggle NYT Crosswords dataset, which contains:
- Clues
- Answers
- Additional metadata

Dataset accessible at: https://www.kaggle.com/datasets/darinhawley/new-york-times-crossword-clues-answers-19932021

Answer length information added ourselves.

## Evaluation Process

1. **Prompt Structure**
   - Each evaluation prompt includes:
     - A batch of fifty crossword clues
     - The lengths of each expected answer
   - Models are instructed to provide a json with the fity answers
   - Exact prompt template:
     ```
     You are solving a crossword puzzle. Given the clues and their answer lengths, provide the correct words.

     {clue_number}. Clue: {clue}
        Length: {length}

     Please provide your answers as a JSON array of strings, in the same order as the clues. Only provide the answer words, with no additional explanation or punctuation.
     ```
   Batches are organized chronologically, meaning that many clues come from the same crossword puzzle in a given batch. The models, not given any information on row, column, clue number, or puzzle, do not seem to incorporate information from other listed clues. We therefore claim that the answers the models provide are fair and independent, with batching just for the purpose of cost minimization.
2. **Scoring**
   - Accuracy is calculated as the percentage of correct answers
   - Answers are case-insensitive
   - Only exact matches are considered correct
   - Detailed results are saved for each evaluation run

3. **Rate Limiting**
   - API calls are rate-limited to prevent hitting API limits
   - Default delay between requests: 0.1 seconds
   - Batch size: 50 clues per API call

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Exact versions:
   ```
   openai>=1.0.0
   anthropic>=0.8.0
   python-dotenv>=1.0.0
   tqdm>=4.65.0
   pandas>=2.0.0
   numpy>=1.24.0
   ```

3. Create a `.env` file based on `.env.template`:
   ```bash
   cp .env.template .env
   ```
4. Add your API keys to the `.env` file:
   - OpenAI API key
   - Anthropic API key
   - DeepSeek API key
   - Set the model name to evaluate

## Running the Benchmark

1. Basic evaluation:
   ```bash
   python src/evaluate.py
   ```

2. The script will:
   - Load the dataset
   - Process each clue
   - Generate model responses
   - Calculate accuracy
   - Save detailed results

## Results




### Model Performance Comparison

| Model | Accuracy | Correct Answers | Total Questions |
|-------|----------|----------------|-----------------|
| GPT-4o (2024-08-06) | 56.86% | 2,843 | 5,000 |
| DeepSeek V3 | 55.08% | 2,754 | 5,000 |

- **Percentage of clues DeepSeek V3 gets correct among those GPT-4o gets correct**: 81.46%
- **Percentage of clues GPT-4o gets correct among those DeepSeek-Chat gets correct**: 84.11%
- **Percentage of clues DeepSeekV3 gets correct among those GPT-4o misses**: 20.90%
- **Percentage of clues GPT-4o gets correct among those DeepSeek-Chat misses**: 24.13%

### Analysis

The benchmark results show interesting variations in model performance:

1. **GPT-4o** leads the pack with a 56.86% accuracy rate

2. **DeepSeek Chat** performs competitively with a 55.08% accuracy rate

### Sample Responses

Here are some example responses from the models:

| Clue | Expected | GPT-4o | DeepSeek Chat | 
|------|----------|---------|---------------|
| "Action done while saying 'Good dog'" | PAT | pet | pat |
| "It might click for a writer" | PEN | pen | pen |
| "Kind to Mother Nature" | ECO | eco | eco |
| "Harris in the Country Music Hall of Fame" | EMMYLOU | emmylou | emmylou |

### Key Observations

1. **Case Sensitivity**: All models' responses are evaluated case-insensitively, which is appropriate for crossword puzzles.

2. **Response Format**: The models generally provide concise, single-word answers as required, though some responses show variations in formatting.

3. **Error Patterns**: Common error types include:
   - Synonyms instead of exact answers
   - Partial matches
   - Different interpretations of clues


## Supported Models and Configuration

All models are configured with the following parameters in `config/model_config.json`:
```json
{
    "rate_limit": 0.1,    // Delay between API calls in seconds
    "max_tokens": 1000,   // Maximum tokens in model response
    "temperature": 0      // Deterministic responses
}
```

Supported Models:
- OpenAI Models:
  - GPT-4
  - GPT-3.5 Turbo
  - GPT-4o
  - GPT-o3
- Anthropic Models:
  - Claude 3 Opus
  - Claude 3 Sonnet
  - Claude 3.5 Sonnet
  - Claude 3.7 Sonnet
  - Claude Opus
- DeepSeek Models:
  - DeepSeek V3
  - DeepSeek R1

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
