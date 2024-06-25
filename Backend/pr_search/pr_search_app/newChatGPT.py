import re
import openai
import json


openai.api_key = ""



def gpt_model(
    query, chatGPT_output_file, model="gpt-3.5-turbo-16k"
):
    print(query)

    # if data to be extracted from the file
    json_filename = "D:\BMC\With_Frontend\Final\Backend\pr_search\data_for_chatgpt.json"

    try:
        with open(json_filename, "r") as json_file:
            pr_data = json.load(json_file)
            # print(pr_data)  # Print to verify data
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    response_data = {}
    i=0
    for pr in pr_data:
        pr_number = pr["number"]
        pr_title = pr["title"]
        pr_labels = pr["labels"]
        pr_body = pr["body"]

        response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that evaluates the relevance of pull request titles to a given query.",
            },
            {
                "role": "user",
                "content": f"Query: {query}\nPR Title: {pr_title}\n \nPR labels: {pr_labels}\n \nRate the relevance of the PR title to the query on a scale from 0 to 1, the scale should have float as a data type and not string",
            },
        ],
    )

        response_content = response['choices'][0]['message']['content']
        # Using regex to extract the first floating-point number from the response content
        match = re.search(r"[-+]?\d*\.\d+|\d+", response_content)
        relevance_score = float(match.group()) if match else 0.0

        # Create response entry
        response_data[str(pr_number)] = {
            "number": pr_number,
            "title": pr_title,
            "score": relevance_score
        }
        i+=1
        print(end=f"\n***********{i}**********\n")

    
    sorted_data = dict(
        sorted(response_data.items(), key=lambda x: x[1]["score"], reverse=True)
    )

    # Save the response to a JSON file
    with open(chatGPT_output_file, 'w') as json_file:
        json.dump(sorted_data, json_file)

    return sorted_data

# Example usage
query = "Update documentation for metrics"


response = gpt_model(query, "chatGPT_output.json")
print(response)
