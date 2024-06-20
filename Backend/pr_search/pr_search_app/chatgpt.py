import sys
import openai
import json
print("hello")
OPENAI_API_KEY = "sk-proj-VxsPrZws8maUAGloF2xMT3BlbkFJ1sxsyykkwAg9IJ0NLK0r" #My key

openai.api_key = OPENAI_API_KEY
chatGPT_output = "chatGPT_output.json"
data_for_chatgpt_filename = "data_for_chatgpt.json"


def chatGPT_top_pr_list(sorted_according_to_pr_number, averaged_sorted_data, n):
    data_for_chatgpt = []
    
    # Create a set of PR numbers from sorted_according_to_pr_number for quick lookup
    pr_numbers = {pr['number'] for pr in sorted_according_to_pr_number}
    total_prs_to_pass_to_gpt = int(len(sorted_according_to_pr_number)*0.7)
    
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
    with open(data_for_chatgpt_filename, mode="w") as json_file:
        json.dump(data_for_chatgpt, json_file, indent=4)
    return data_for_chatgpt


def generate_json_response(prompt, pr_data, max_tokens=15500):
    # Include query and PR data in the prompt
    full_prompt = prompt + " " + json.dumps(pr_data)

    # Ensure the total tokens (input + output) do not exceed the model's limit
    prompt_tokens = len(full_prompt.split())
    max_tokens = min(max_tokens, 16385 - prompt_tokens)

    if prompt_tokens >= 16385:
        raise ValueError("Prompt is too long, please shorten the prompt.")

    # Generate the completion using the provided prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "user", "content": full_prompt}],
        max_tokens=max_tokens,
    )

    return response.choices[0].message["content"].strip()



def chatGPT_model(query, data_for_chatgpt ,output_json_filename):
    # query = input("Enter a query: ")
    prompt = query +r""" is the query provided by the user.
Please provide a valid response in the exact format of JSON. Your query is about calculating similarity, such as cosine similarity, for each pull request (PR) in the provided JSON file compared to the query. Arrange the PRs in descending order based on their similarity scores. The resulting JSON should include 'number', 'title', 'rank', and 'similarity_score' for each PR. 

{
    "88115": {
        "number": 88115,
        "title": "Docs/usman plugin mgmt",
        "score": 0.369,
    }
}

"""
    
    # json_filename = "D:\BMC\With_Frontend\Final\Backend\pr_search\data_for_chatgpt.json"
    output_json_filename = "ssss.json"
    # Load JSON data from file
    
    # try:
    #     with open(json_filename, "r") as json_file:
    #         data_for_chatgpt = json.load(json_file)
    #         print(data_for_chatgpt)  # Print to verify data
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")
    
    print(data_for_chatgpt, end="---")
    # Generate JSON response
    results = {}
    for pr in data_for_chatgpt:
        try:
            response = generate_json_response(prompt, pr)
            response_json = json.loads(response)
            results[pr['number']] = response_json
        except Exception as e:
            print(f"Error processing PR {pr['number']}: {e}")
            continue
    
    # Save JSON response to a file
    
    # Sort by average value in descending order
    sorted_data = dict(sorted(results.items(), key=lambda x: x[1]["score"], reverse=True))

    # Add rank attribute based on sorted order
    rank = 1
    for key, value in sorted_data.items():
        value["rank"] = rank
        rank += 1


    with open(output_json_filename, "w") as json_file:
        json.dump(sorted_data, json_file, indent=4)

    # return sorted_data

    # json_response = generate_json_response(prompt, data_for_chatgpt)
    # # Save JSON response to a file
    # save_to_json(json.loads(json_response), output_json_filename)
    # return json.loads(json_response)


    
# chatGPT_model("performance bottleneck")











