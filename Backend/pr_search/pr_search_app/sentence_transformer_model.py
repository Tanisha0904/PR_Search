from sentence_transformers import util
from collections import defaultdict


def merge_pr_data(sorted_according_to_pr_number):

    documents = {}
    for fact in sorted_according_to_pr_number:
        if fact["body"] is not None:
            doc_text = (
                fact["title"] + " " + fact["body"] + " " + " ".join(fact["labels"])
            )
        else:
            doc_text = fact["title"] + " " + " ".join(fact["labels"])

        documents[fact["number"]] = doc_text
    return documents

# Function to compute similarity scores
def compute_similarity(query, documents, threshold, model):
    query_embedding = model.encode(query, convert_to_tensor=True)
    similarity_scores = defaultdict(float)

    for doc_number, doc_text in documents.items():
        doc_embedding = model.encode(doc_text, convert_to_tensor=True)
        sim = util.pytorch_cos_sim(query_embedding, doc_embedding).item()

        if sim > threshold:
            similarity_scores[doc_number] = sim
    return similarity_scores



# Main function to process and search the documents
def sentence_transformer_model(query, documents, model, modelName):
    # threshold = float(input("enter the similarity threshold:"))
    threshold=-1 #set to -1 so that all the PRs are retrieved, to limit the number of prs, this can be changed and also taken from the user as input


    similarity_scores = compute_similarity(query, documents, threshold, model)
    # sorting according to the similarity score
    results = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)

    print(f"{modelName} done...")
    
    return results

    
    
