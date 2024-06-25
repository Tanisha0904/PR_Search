import openai
import json
from .secrets_1 import OPENAI_API_KEY 

openai.api_key = OPENAI_API_KEY
chatGPT_output = "chatGPT_output.json"
data_for_chatgpt_filename = "data_for_chatgpt.json"


def gpt_top_pr_list(sorted_according_to_pr_number, averaged_sorted_data, n):
    data_for_chatgpt = []
    
    # Create a set of PR numbers from sorted_according_to_pr_number for quick lookup
    pr_numbers = {pr['number'] for pr in sorted_according_to_pr_number}
    total_prs_to_pass_to_gpt = int(len(sorted_according_to_pr_number)*0.5) #passing the top 50% prs to gpt
    # total_prs_to_pass_to_gpt = 50
    
    for value in averaged_sorted_data.values():
        if value["rank"] <= total_prs_to_pass_to_gpt and value["number"] in pr_numbers:
            for pr in sorted_according_to_pr_number:
                if pr['number'] == value['number']:
                    data_for_chatgpt.append({
                        "number": pr['number'],
                        "title": pr['title'],
                        "body": pr['body'],
                        "labels": pr['labels']
                    })
                    break
        else:
            break #beacuse the data is sorted according the rank/average scores
        
    with open(data_for_chatgpt_filename, mode="w") as json_file:
        json.dump(data_for_chatgpt, json_file, indent=4)
    return data_for_chatgpt










