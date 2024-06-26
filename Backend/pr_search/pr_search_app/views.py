
import re
import urllib.parse
import traceback
import logging
from sentence_transformers import SentenceTransformer
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
from django.http import JsonResponse
from .all_combined import gpt_model_combined
import openai 
from .methodsToSearchDocuments import get_pr_number_list, clear_file, get_response_from_version_compare_api, read_data_from_json
from .sentence_transformer_model import merge_pr_data, sentence_transformer_model
from .spacy_model import spacy_model
from .secrets_1 import GITHUB_TOKEN, OPENAI_API_KEY
from .tag_list import get_tag_list
from .jsonData import comparisonData_json, averagedData_json, calculate_average_scores, json_data
from .chatgpt import gpt_top_pr_list, chatGPT_output, data_for_chatgpt_filename

openai.api_key = OPENAI_API_KEY
token = GITHUB_TOKEN
# Configure logging
logger = logging.getLogger(__name__)

def index(request):
    return render(request, "pr_search_app/index.html")

@csrf_exempt  
def get_versions(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            owner_ = data.get("owner")
            repo_ = data.get("repo")
        
            owner = urllib.parse.quote(owner_)
            repo = urllib.parse.quote(repo_)
            
            versions = get_tag_list(owner, repo)
            return JsonResponse(versions, safe=False)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)



def gpt_model(
    query, chatGPT_output_file, pr_data, model="gpt-3.5-turbo-16k"
):
    print(query)

    # # if data to be extracted from the file
    # json_filename = "D:\BMC\With_Frontend\Final\Backend\pr_search\data_for_chatgpt.json"

    # try:
    #     with open(json_filename, "r") as json_file:
    #         pr_data = json.load(json_file)
    #         # print(pr_data)  # Print to verify data
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")

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
                "content": f"Query: {query}\nPR Title: {pr_title}\n \nPR labels: {pr_labels}\n \nPR body: {pr_body}\nRate the relevance of the PR title to the query on a scale from 0 to 1, the scale should have float as a data type and not string",
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

    # # Save the response to a JSON file
    # with open(chatGPT_output_file, 'w') as json_file:
    #     json.dump(sorted_data, json_file)

    return sorted_data


def gpt(query, n, sorted_according_to_pr_number, averaged_sorted_data={}):
    if averaged_sorted_data=={}:

        print("only gpt")
        data_for_chatgpt = sorted_according_to_pr_number

        
            
    else:
        print("both")

        clear_file(data_for_chatgpt_filename)

        data_for_chatgpt=gpt_top_pr_list(sorted_according_to_pr_number, averaged_sorted_data, n)
    
    clear_file(chatGPT_output)

    # results=gpt_model(query, chatGPT_output, data_for_chatgpt) # sending the PRs one by one

    results=gpt_model_combined(query, chatGPT_output, data_for_chatgpt) #send ing all PRs at once

    return results
    


def llm(query, documents, doc_numbers_to_titles):
    print("llm")
    
    # clear the data on the file if any was stored previously 
    clear_file(comparisonData_json)
    clear_file(averagedData_json)
    
    model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L12-v2"
            )
    all_MiniLM_L12_result = sentence_transformer_model(
                query, 
                documents, 
                model, 
                "all_MiniLM_L12"
            )
    json_data(all_MiniLM_L12_result, doc_numbers_to_titles, "all_MiniLM_L12")
    
            
    model = SentenceTransformer(
                "sentence-transformers/paraphrase-distilroberta-base-v1"
            )
    paraphrase_distilroberta_result=sentence_transformer_model(
                query,
                documents,
                model,
                "paraphrase_distilroberta",
            )
    json_data(paraphrase_distilroberta_result, doc_numbers_to_titles, "paraphrase_distilroberta")

    model = SentenceTransformer(
                "sentence-transformers/msmarco-distilroberta-base-v2"
            )
    msmarco_distilroberta_result = sentence_transformer_model(
                query,
                documents,
                model,
                "msmarco_distilroberta",
            )
    json_data(msmarco_distilroberta_result, doc_numbers_to_titles, "msmarco_distilroberta")

    model = SentenceTransformer("sentence-transformers/quora-distilbert-base")
    quora_distilbert_result = sentence_transformer_model(
                query,
                documents,
                model,
                "quora_distilbert",
            )
    json_data(quora_distilbert_result, doc_numbers_to_titles, "quora_distilbert")

    spacy_model_result = spacy_model(
                query, 
                documents
            )
    
    json_data(spacy_model_result, doc_numbers_to_titles, "spacy_model")









            
           
    averaged_sorted_data = calculate_average_scores()
    return averaged_sorted_data
    



@csrf_exempt
def search_documents(request):
    print("in search_documents")

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            query = data.get("query")
            base_version = data.get("baseVersion")
            compare_version = data.get("compareVersion")
            owner_ = data.get("owner")
            repo_ = data.get("repo")
            n = int(data.get("n"))
            selectedOption = data.get("selectedOption")
            
            # parsing the string(so that symbols are included in the stirng)
            owner = urllib.parse.quote(owner_)
            repo = urllib.parse.quote(repo_)

            file_name = f"{base_version}_{compare_version}_pr_list.json"

            api_response = get_response_from_version_compare_api(
                owner, repo, base_version, compare_version
            )

            if api_response:
                sorted_according_to_pr_number = get_pr_number_list(owner, repo, api_response, file_name)
            else:
                logger.error("Failed to fetch the commits data.")
                return JsonResponse({"error": "Failed to fetch the commits data."}, status=500)

            # pass the pr data to the models individually
            doc_numbers_to_titles = {fact["number"]: fact["title"] for fact in sorted_according_to_pr_number}

            documents = merge_pr_data(sorted_according_to_pr_number)


            if selectedOption == "gpt":
                print("---only gpt")
                results= gpt(query, n, sorted_according_to_pr_number)
                
            
            else:
                
                averaged_sorted_data = llm(query, documents, doc_numbers_to_titles)
                if selectedOption == "llm":
                    print("---only llm")
                    results = averaged_sorted_data


                elif selectedOption == "both":
                    print("---both")
                    results = gpt(query, n, sorted_according_to_pr_number, averaged_sorted_data)


            return read_data_from_json(results, n, owner, repo) 
            

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)
