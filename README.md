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
     - The crossword clue
     - The length of the expected answer
   - Models are instructed to provide only the answer word
   - Exact prompt template:
     ```
     You are solving a crossword puzzle. Given the clues and their answer lengths, provide the correct words.

     {clue_number}. Clue: {clue}
        Length: {length}

     Please provide your answers as a JSON array of strings, in the same order as the clues. Only provide the answer words, with no additional explanation or punctuation.
     ```

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

Results are saved in the `results` directory with the following information:
- Model name
- Overall accuracy
- Total questions attempted
- Number of correct answers
- Detailed results for each question

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

## Best Practices

1. Monitor API usage and costs
2. Save results regularly
3. Use appropriate rate limiting for your API tier
4. Check API documentation for any model-specific limitations or requirements

## License

This project is licensed under the MIT License - see the LICENSE file for details. 