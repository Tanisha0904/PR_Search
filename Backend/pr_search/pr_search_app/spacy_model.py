import csv
import json
import spacy
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict


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



def spacy_model(query, merged_documents):

    documents = {}
    for pr_number, doc_text in merged_documents.items():
        doc = nlp(doc_text)
        tokens = [
            word.text.lower()
            for word in doc
            if not word.is_stop and not word.is_punct
        ]
        documents[pr_number] = " ".join(tokens)

    similarity_scores = compute_similarity(query, documents)
    results = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)
    
    print("spacy done...")
    return results
