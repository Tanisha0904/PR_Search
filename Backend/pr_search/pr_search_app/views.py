import csv
import os
import urllib.parse
import traceback
import logging
from sentence_transformers import SentenceTransformer
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.conf import settings
from .methodsToSearchDocuments import get_pr_number_list, clear_file, get_response_from_version_compare_api, read_data_from_json
from .sentence_transformer_model import sentence_transformer_model
from .spacy_model import spacy_model
from .secrets_1 import GITHUB_TOKEN
from .tag_list import get_tag_list
from .csvData import comparisonData_csv
from .jsonData import comparisonData_json, averagedData_json, calculate_average_scores, json_data, chatGPT_top_pr_list


token = GITHUB_TOKEN
# Configure logging
logger = logging.getLogger(__name__)

def index(request):
    return render(request, "pr_search_app/index.html")

@csrf_exempt  # Apply CSRF exemption to allow POST requests without CSRF token
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


@csrf_exempt
def search_documents(request):

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            query = data.get("query")
            base_version = data.get("baseVersion")
            compare_version = data.get("compareVersion")
            owner_ = data.get("owner")
            repo_ = data.get("repo")
            n = int(data.get("n"))
            
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
            # print(doc_numbers_to_titles)

            model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L12-v2"
            )
            all_MiniLM_L12_result = sentence_transformer_model(
                query, 
                sorted_according_to_pr_number, 
                model, 
                "all_MiniLM_L12"
            )
            
            # model = SentenceTransformer(
            #     "sentence-transformers/paraphrase-distilroberta-base-v1"
            # )
            # paraphrase_distilroberta_result=sentence_transformer_model(
            #     query,
            #     sorted_according_to_pr_number,
            #     model,
            #     "paraphrase_distilroberta",
            # )

            # model = SentenceTransformer(
            #     "sentence-transformers/msmarco-distilroberta-base-v2"
            # )
            # msmarco_distilroberta_result = sentence_transformer_model(
            #     query,
            #     sorted_according_to_pr_number,
            #     model,
            #     "msmarco_distilroberta",
            # )

            # model = SentenceTransformer("sentence-transformers/quora-distilbert-base")
            # quora_distilbert_result = sentence_transformer_model(
            #     query,
            #     sorted_according_to_pr_number,
            #     model,
            #     "quora_distilbert",
            # )

            # spacy_model_result = spacy_model(
            #     query, 
            #     sorted_according_to_pr_number
            # )

            # clar the data on the file if any was stored previously 
            clear_file(comparisonData_json)
            clear_file(averagedData_json)
             
            json_data(all_MiniLM_L12_result, doc_numbers_to_titles, "all_MiniLM_L12")
            # input("=====")

            # json_data(quora_distilbert_result, doc_numbers_to_titles, "quora_distilbert")
            # # input("=====")
            # json_data(msmarco_distilroberta_result, doc_numbers_to_titles, "msmarco_distilroberta")
            # # input("=====")
            # json_data(paraphrase_distilroberta_result, doc_numbers_to_titles, "paraphrase_distilroberta")
            # # input("=====")
            # json_data(spacy_model_result, doc_numbers_to_titles, "spacy_model")
           
            averaged_sorted_data = calculate_average_scores()

            return read_data_from_json(averaged_sorted_data, n, owner, repo) #without chatgpt
        
            # chatGPT_sorted_data=chatGPT_top_pr_list(sorted_according_to_pr_number, averaged_sorted_data)
            # return read_data_from_json(chatGPT_sorted_data, n, owner, repo) #with chatgpt

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)
