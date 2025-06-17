import json

def load_results(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def calculate_correct_and_missed_percentages(model1_results, model2_results):
    model1_correct_clues = {result['clue'] for result in model1_results['detailed_results'] if result['is_correct']}
    model2_correct_clues = {result['clue'] for result in model2_results['detailed_results'] if result['is_correct']}
    
    # Calculate percentage of model1 correct among model2 correct
    common_correct_clues = model1_correct_clues.intersection(model2_correct_clues)
    if len(model2_correct_clues) > 0:
        model1_among_model2_percentage = (len(common_correct_clues) / len(model2_correct_clues)) * 100
    else:
        model1_among_model2_percentage = 0

    # Calculate percentage of model2 correct among model1 correct
    if len(model1_correct_clues) > 0:
        model2_among_model1_percentage = (len(common_correct_clues) / len(model1_correct_clues)) * 100
    else:
        model2_among_model1_percentage = 0

    # Calculate percentage of model1 correct among model2 missed
    model2_missed_clues = {result['clue'] for result in model2_results['detailed_results'] if not result['is_correct']}
    model1_among_model2_missed_percentage = (len(model1_correct_clues.intersection(model2_missed_clues)) / len(model2_missed_clues)) * 100 if len(model2_missed_clues) > 0 else 0

    # Calculate percentage of model2 correct among model1 missed
    model1_missed_clues = {result['clue'] for result in model1_results['detailed_results'] if not result['is_correct']}
    model2_among_model1_missed_percentage = (len(model2_correct_clues.intersection(model1_missed_clues)) / len(model1_missed_clues)) * 100 if len(model1_missed_clues) > 0 else 0

    return (model1_among_model2_percentage, model2_among_model1_percentage, 
            model1_among_model2_missed_percentage, model2_among_model1_missed_percentage)

# Load results
deepseek_chat_results = load_results('benchmark/results/deepseek-chat_results.json')
gpt_4o_results = load_results('benchmark/results/gpt-4o-2024-08-06_results.json')

# Calculate percentages
(deepseek_among_gpt4o, gpt4o_among_deepseek, 
 deepseek_among_gpt4o_missed, gpt4o_among_deepseek_missed) = calculate_correct_and_missed_percentages(deepseek_chat_results, gpt_4o_results)

# Output results
print(f"Percentage of clues DeepSeek-Chat gets correct among those GPT-4o gets correct: {deepseek_among_gpt4o:.2f}%")
print(f"Percentage of clues GPT-4o gets correct among those DeepSeek-Chat gets correct: {gpt4o_among_deepseek:.2f}%")
print(f"Percentage of clues DeepSeek-Chat gets correct among those GPT-4o misses: {deepseek_among_gpt4o_missed:.2f}%")
print(f"Percentage of clues GPT-4o gets correct among those DeepSeek-Chat misses: {gpt4o_among_deepseek_missed:.2f}%")
