import openai
import json


openai.api_key = "sk-proj-2deaBZKpY8XzJRgUp8GdT3BlbkFJmAFhYzDSaI1vL0eaJWq3"


def evaluate_relevance(query, pr_title, pr_labels, pr_body, model="gpt-3.5-turbo-16k"):
    """
    Use a GPT model to evaluate the relevance of a PR title to the query.
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
                "content": f"Query: {query}\nPR Title: {pr_title}\n \nPR labels: {pr_labels}\n \nPR body: {pr_body}\nRate the relevance of the PR title to the query on a scale from 0 to 1",
            },
        ],
    )
    relevance_score = float(response['choices'][0]['message']['content'])
    return relevance_score


def chatGPT_model_new(
    query, chatGPT_output_file, model="gpt-3.5-turbo-16k"
):
    print(query)
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

        # Evaluate relevance score using the GPT model
        # relevance_score = evaluate_relevance(query, pr_title,  pr_labels, pr_body, model)

        response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that evaluates the relevance of pull request titles to a given query.",
            },
            {
                "role": "user",
                "content": f"Query: {query}\nPR Title: {pr_title}\n \nPR labels: {pr_labels}\n \nPR body: {pr_body}\nRate the relevance of the PR title to the query on a scale from 0 to 1",
            },
        ],
    )
        relevance_score = float(response['choices'][0]['message']['content'])

        # Create response entry
        response_data[str(pr_number)] = {
            "number": pr_number,
            "title": pr_title,
            "score": relevance_score
        }
        i+=1
        print(response_data,end=f"\n***********{i}**********\n")

    # Save the response to a JSON file
    sorted_data = dict(
        sorted(response_data.items(), key=lambda x: x[1]["score"], reverse=True)
    )
    with open(chatGPT_output_file, 'w') as json_file:
        json.dump(sorted_data, json_file)

    return sorted_data


# Example usage
# query = "Update documentation for metrics"


# response = chatGPT_model_new(query, "chatGPT_output.json")
# print(response)
