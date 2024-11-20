import csv
import pandas as pd
from MCQgeneration import generateMCQ
import re


import re

def parse_mcq(mcq_text):
    # Split the text into lines and remove empty ones
    lines = [line.strip() for line in mcq_text.strip().split('\n') if line.strip()]
    
    # Extract question
    question = re.search(r"Question: (.+)", lines[1]).group(1)
    
    # Extract options
    options = {line[0]: line[3:] for line in lines[2:6]}  # A-D options
    
    # Extract correct answer
    correct_answer_key = re.search(r"Correct Answer: (.+)", lines[6]).group(1)
    correct_answer = options[correct_answer_key]
    
    return [question, options['A'], options['B'], options['C'], options['D'], correct_answer]


def process_dataset_and_generate_mcqs(dataframe, number_of_questions=1):
    """
    This function processes each entry in the 'Text' column of the given DataFrame using
    the generateMCQ function. It then saves the output in a new CSV file.
    
    :param dataframe: pandas DataFrame containing a 'Text' column
    :param number_of_questions: Number of MCQs to generate for each text entry
    """
    results = []

    for index, row in dataframe.iterrows():
        try:
            text = row['Text']
            # Call the generateMCQ function
            generated_mcq = generateMCQ(text, number_of_questions)
            
            parsed_mcq = parse_mcq(generated_mcq)
            
            results.append(parsed_mcq)
        except Exception as e:
            print(f"Error processing row {index}: {e}")
        # break

    results_df = pd.DataFrame(results, columns=["Question", "Option 1", "Option 2", "Option 3", "Option 4", "Correct Answer"])
    # print(results)
    return results_df

# Load the dataset
file_path = 'data.csv'
dataset = pd.read_csv(file_path)

# process_dataset_and_generate_mcqs(dataset,1)
# Process the dataset
results_df = process_dataset_and_generate_mcqs(dataset, number_of_questions=1)
print(results_df)

# Save the results to a CSV file
results_df.to_csv('Generated_MCQs.csv', index=False)
print("MCQs saved to Generated_MCQs.csv.")
