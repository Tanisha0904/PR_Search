import csv
from collections import defaultdict

comparisonData_csv = "ComparisonData.csv"
comparisonData_fieldnames = [
    "number",
    "title",
    "spacy_model",
    "all_MiniLM_L12",
    "paraphrase_distilroberta",
    "msmarco_distilroberta",
    "quora_distilbert",
    "zero_shot",
]

# Function to read existing CSV data into a dictionary
def read_existing_data(csv_file_path):
    data = defaultdict(dict)
    try:
        with open(csv_file_path, mode="r", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                number = row["number"]
                for field in comparisonData_fieldnames[1:]:
                    if field in row and row[field]:
                        try:
                            data[number][field] = float(row[field])
                        except ValueError:
                            data[number][field] = row[field]  # Keep the original value if it's not a float
    except FileNotFoundError:
        pass  # If file doesn't exist, return empty data
    return data

# Function to write updated data to CSV
def write_updated_data(csv_file_path, data, doc_numbers_to_titles, modelName):
    with open(csv_file_path, mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=comparisonData_fieldnames)
        writer.writeheader()
        for number, scores in data.items():
            row = {"number": number, "title": doc_numbers_to_titles.get(number)}
            for field in comparisonData_fieldnames[2:]:
                row[field] = scores.get(field, "")
            writer.writerow(row)

def csvData(results, doc_numbers_to_titles, modelName):
    # Read existing data
    existing_data = read_existing_data(comparisonData_csv)

    # Update existing data with new results
    for doc_number, similarity_score in results:
        if doc_number in doc_numbers_to_titles:
            try:
                existing_data[doc_number][modelName] = float(similarity_score)
            except ValueError:
                print(f"Invalid similarity score for document {doc_number}: {similarity_score}")
        else:
            print(f"Document with number {doc_number} does not exist in the data.")

    # Write updated data back to CSV
    write_updated_data(comparisonData_csv, existing_data, doc_numbers_to_titles, modelName)


'''
# Example usage:
results_1 = [
    ("1", 0.9),
    ("2", 0.85),
    ("3", 0.78),
    ("4", 0.92),
    ("5", 0.88),
    ("6", 0.81),
    ("7", 0.76),
    ("8", 0.95),
    ("9", 0.83),
    ("10", 0.87)
]
results_2 = [
    ("1", 0.91),
    ("2", 0.84),
    ("3", 0.77),
    ("4", 0.93),
    ("5", 0.89),
    ("6", 0.80),
    ("7", 0.75),
    ("8", 0.96),
    ("9", 0.82),
    ("10", 0.86)
]

doc_numbers_to_titles = {
    "1": "Title 1",
    "2": "Title 2",
    "3": "Title 3",
    "4": "Title 4",
    "5": "Title 5",
    "6": "Title 6",
    "7": "Title 7",
    "8": "Title 8",
    "9": "Title 9",
    "10": "Title 10"
}

csvData(results_1, doc_numbers_to_titles, "spacy_model")
input()
csvData(results_2, doc_numbers_to_titles, "all_MiniLM_L12")
# csvData(results_3, doc_numbers_to_titles, "spacy_model")
# csvData(results_4, doc_numbers_to_titles, "spacy_model")

'''