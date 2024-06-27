import re
import openai
import json
from .secrets_1 import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def gpt_model_combined(query, chatGPT_output_file,pr_data, model="gpt-3.5-turbo-16k"):
    print(query)

    # # If data to be extracted from the file
    # json_filename = "D:\BMC\openai\data_for_chatgpt1.json"

    # try:
    #     with open(json_filename, "r") as json_file:
    #         pr_data = json.load(json_file)
    #         # print(pr_data)  # Print to verify data
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")

    # Combine all PR data into a single message
    pr_combined_data = "\n".join(
        [
            f"PR Number: {pr['number']}\nPR Title: {pr['title']}\nPR Labels: {pr['labels']}"
            for pr in pr_data
        ]
    )

    # Create a prompt that includes all PR data
    prompt = f"""
    You are an assistant that evaluates the relevance(similarity score) of pull request(PR) content to a given query.
     
    Query: {query}
    
    Here is a list of PRs. Treat every PR separately such that no PR is related to the other PRs while finding the relevance. Rate the relevance of the PR title to the query on a scale from 0 to 1. The scale should have float as a data type and not string and it can be precise to 4 decimal points. No result will have score 1 unless the content of PR is exactly same as the query.
    {pr_combined_data}

    Return the output in the following format so that it can be stored as json data and can be used for further processing:
    {{
      "PR1 Number": {{
        "number": PR1 Number,
        "title": PR1 Title,
        "score": float(Relevance Score of PR1)
      }},
      "PR2 Number": {{
        "number": PR2 Number,
        "title": PR2 Title,
        "score": float(Relevance Score of PR2)
      }},
      ...
    }}
    Here replace the PR Number, PR Title, and Relevance Score of PR with the respective data that will be unique for each PR. Just return the expected results in json format. Nothing else is needed, no code, no introductiory statemnts, no conclusions, etc. Just the JSON format output
    """

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that evaluates the relevance of pull request titles to a given query.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    response_content = response["choices"][0]["message"]["content"]
    print(response_content, end="~~~~~~~~~~~~~/n")

    # Attempt to parse the JSON response from the model's output
    try:
        parsed_response = json.loads(response_content)
    except json.JSONDecodeError:
        print(
            "Failed to decode JSON from the model's response. Attempting to parse manually."
        )
        # Attempt manual parsing
        parsed_response = manual_parse_response(response_content)

    # Ensure the data is sorted by score
    sorted_data = dict(
        sorted(parsed_response.items(), key=lambda x: x[1]["score"], reverse=True)
    )

    # Save the response to a JSON file
    with open(chatGPT_output_file, "w") as json_file:
        json.dump(sorted_data, json_file)

    return sorted_data


def manual_parse_response(response_content):
    """
    Manually parse the response content to extract PR data and scores.
    This is a fallback in case the response is not valid JSON.
    """
    print("in manual_parse_response")
    pr_data = {}
    pr_entries = re.split(
        r"\}\s*,\s*\{", response_content
    )  # Split entries more accurately

    for entry in pr_entries:
        try:
            match = re.search(r'"number": (\d+)', entry)
            pr_number = match.group(1) if match else None

            match = re.search(r'"title": "([^"]+)"', entry)
            pr_title = match.group(1) if match else None

            match = re.search(r'"score": ([0-1]\.\d+)', entry)
            relevance_score = float(match.group(1)) if match else None

            if pr_number and pr_title and relevance_score is not None:
                pr_data[pr_number] = {
                    "number": int(pr_number),
                    "title": pr_title,
                    "score": relevance_score,
                }
            print(f"----{pr_data[pr_number]}----\n")
        except Exception as e:
            print(f"Error parsing entry: {entry} - {e}")

    return pr_data


# # Example usage
# query = "json tokens"

# response = gpt_model_combined(query, "all_combined_chatGPT_output1.json")
# # print(response)
