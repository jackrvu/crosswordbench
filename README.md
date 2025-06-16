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

2. **Scoring**
   - Accuracy is calculated as the percentage of correct answers
   - Answers are case-insensitive
   - Only exact matches are considered correct
   - Detailed results are saved for each evaluation run

3. **Rate Limiting**
   - API calls are rate-limited to prevent hitting API limits
   - Configurable delay between requests

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
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

## Supported Models
- GPT-o3
- GPT-4o
- GPT-4
- GPT-3.5 Turbo
- Claude 3 Opus
- Claude 3 Sonnet
- Claude 3.5 Sonnet
- Claude 3.7 Sonnet
- Claude Opus
- DeepSeek V3
- DeepSeek R1

## Configuration

Model-specific settings can be adjusted in `config/model_config.json`:
- Rate limiting
- Maximum tokens
- Temperature
- Other model-specific parameters

## Best Practices

1. Start with a small sample size for testing
2. Monitor API usage and costs
3. Save results regularly
4. Use appropriate rate limiting for your API tier

## License

This project is licensed under the MIT License - see the LICENSE file for details. 