import csv
import json
import spacy
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

from .jsonData import json_data
from .csvData import csvData

nlp = spacy.load("en_core_web_md")


# Tokenize and vectorize the query
def preprocess_query(query):
    doc = nlp(query)
    tokens = [
        word.text.lower() for word in doc if not word.is_stop and not word.is_punct
    ]
    return " ".join(tokens)


# Compute cosine similarity between the query and each document
def compute_similarity(query, documents):
    query_vector = nlp(preprocess_query(query)).vector

    similarity_scores = defaultdict(float)
    # threshold = float(input("enter the similarity threshold:"))
    threshold=-1
    for doc_number, doc_text in documents.items():
        doc_vector = nlp(doc_text).vector
        sim = cosine_similarity([query_vector], [doc_vector])[0][0]

        if sim > threshold:
            similarity_scores[doc_number] = float(sim)
    return similarity_scores



def spacy_model(query, sorted_according_to_pr_number):

    doc_numbers_to_titles = {fact["number"]: fact["title"] for fact in sorted_according_to_pr_number}

    # Preprocess the data and tokenize the text
    documents = {}
    for fact in sorted_according_to_pr_number:

        if fact["body"] is not None:
            doc = nlp(
                fact["title"] + " " + fact["body"] + " " + " ".join(fact["labels"])
            )
        else:
            doc = nlp(fact["title"] + " " + " ".join(fact["labels"]))

        tokens = [
            word.text.lower()
            for word in doc
            if not word.is_stop and not word.is_punct
        ]
        documents[fact["number"]] = " ".join(tokens)


    similarity_scores = compute_similarity(query, documents)
    results = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)
    
    print("spacy done...")
    return results
    # csvData(results, doc_numbers_to_titles, "spacy_model")
    json_data(results, doc_numbers_to_titles, "spacy_model")
    
