import json
from collections import defaultdict
import os

comparisonData_json = "ComparisonData.json"
averagedData_json="AveragedData.json"
def json_data(results, doc_numbers_to_titles, modelName):
    # print(doc_numbers_to_titles, end="------------\n")

    try:
        if os.path.exists(comparisonData_json):
            with open(comparisonData_json, mode="r") as json_file:
                existing_data = json.load(json_file)
        else:
            existing_data = defaultdict(dict)
    except json.JSONDecodeError:
        existing_data = defaultdict(dict)

    for doc_number, similarity_score in results:
        # doc_number_str = str(doc_number)
        if doc_number in doc_numbers_to_titles:
            doc_number_str = str(doc_number)
            if doc_number_str in existing_data:
                existing_data[doc_number_str]["scores"][modelName] = similarity_score
            else:
                existing_data[doc_number_str] = {
                    "number": doc_number,
                    "title": doc_numbers_to_titles.get(doc_number, ""),
                    "scores": {modelName: similarity_score}
                }
        else:
            print(f"Document with number {doc_number} does not exist in the data.")

    # Write updated data back to JSON
    with open(comparisonData_json, mode="w") as json_file:
        json.dump(existing_data, json_file, indent=4)
    
    print(f"{modelName} model data stored to json!")

def calculate_average_scores():
    with open(comparisonData_json, 'r') as file:
        json_data = json.load(file)
    
    for key, value in json_data.items():
        scores = value["scores"]
        average = sum(scores.values()) / len(scores)
        value["average"] = round(average, 3)

    # Sort by average value in descending order
    sorted_data = dict(sorted(json_data.items(), key=lambda x: x[1]["average"], reverse=True))

    # Add rank attribute based on sorted order
    rank = 1
    for key, value in sorted_data.items():
        value["rank"] = rank
        rank += 1
    
    with open(averagedData_json, mode="w") as json_file:
        json.dump(sorted_data, json_file, indent=4)
    
    return sorted_data


# def chatGPT_top_pr_list(sorted_according_to_pr_number, averaged_sorted_data):
#     for key, value in averaged_sorted_data.items():
#         if value["rank"] <= 50 :
#             if value["number"] in sorted_according_to_pr_number.items()["number"]:
#                 data_for_chatgpt.append = the particular items from the 







    return None

'''
# Example usage:
sample = [
    (83790, 0.31422746181488037), (82713, 0.2899104952812195), (82939, 0.2812437415122986), 
    (83731, 0.25869905948638916), (82438, 0.2584773898124695), (83837, 0.251043438911438), 
    (82731, 0.24634064733982086), (82147, 0.2452625036239624), (82221, 0.24439950287342072), 
    (82350, 0.22166338562965393), (83612, 0.21935638785362244), (82930, 0.21288879215717316), 
    (83105, 0.19089797139167786), (83725, 0.19051828980445862), (82445, 0.1901351511478424), 
    (81959, 0.18449032306671143), (83428, 0.18446752429008484), (83553, 0.16817373037338257), 
    (83055, 0.1601206362247467), (82537, 0.14705786108970642), (81862, 0.1365465372800827), 
    (83936, 0.13515843451023102), (83244, 0.13034266233444214), (82432, 0.12711253762245178), 
    (83683, 0.12674015760421753), (81929, 0.11351840198040009), (83213, 0.10694627463817596), 
    (82320, 0.1038704663515091), (82164, 0.10267145931720734), (83750, 0.09668224304914474), 
    (83052, 0.09553959220647812), (83680, 0.09544754028320312), (82356, 0.09134349226951599), 
    (82877, 0.088422492146492), (81809, 0.0777057409286499), (82238, 0.07593788206577301), 
    (83203, 0.0736449807882309), (83484, 0.07176260650157928), (83142, 0.07020324468612671), 
    (83177, 0.06832636892795563), (83722, 0.06386023014783859), (83702, 0.06111555173993111), 
    (82244, 0.059907615184783936), (82055, 0.05927632004022598), (82240, 0.05726636201143265), 
    (82402, 0.05309808999300003), (82103, 0.05260281264781952), (82039, 0.04576371610164642), 
    (83141, 0.04383033514022827), (82400, 0.04059268534183502), (82902, 0.038492023944854736), 
    (81983, 0.03625619783997536), (82259, 0.026294250041246414), (81954, 0.022234588861465454), 
    (83525, 0.022119563072919846), (83405, 0.012007083743810654), (82561, -0.0030596740543842316), 
    (83596, -0.009123828262090683), (83325, -0.04324580729007721), (81463, -0.11247570067644119)
]

doc_sample = {
    "81463": '[v10.3.x] Loki/Elastic: Assert queryfix value to always be string',
    "81809": '[v10.3.x] Docs: Restructure configure thresholds docs',
    "81862": '[v10.3.x] Folders: Fix failure to update folder in SQLite',
    "81929": "[v10.3.x] Elasticsearch: Set middlewares from Grafana's `httpClientProvider`",
    "81954": '[v10.3.x] Docs: remove disable scaling units entry',
    "81959": '[v10.3.x] Remove X-Grafana-Device-Id from outbound requests',
    "81983": '[v10.3.x] ShareModal: Remove shareView param when creating a sharing URL',
    "82039": '[v10.3.x] Alerting: Update legacy migration docs to include Upgrade Preview',
    "82055": '[v10.3.x] Alerting docs: changes alerting rules to alert rules',
    "82103": '[v10.3.x] Add missing step',
    "82147": "[v10.3.x] Plugins: Don't auto prepend app sub url to plugin asset paths",
    "82164": '[v10.3.x] Doc: Custom branding is not applicable to OSS',
    "82221": 'Alerting docs: `Provision alerting resources` updates',
    "82238": '[v10.3.x] Update `make docs` procedure',
    "82240": '[v10.3.x] Docs: Update default value of rbac.permission_validation_enabled',
    "82244": '[v10.3.x] Update RBAC role name: fixed:datasources.id:reader',
    "82259": '[v10.3.x] LibraryPanels: Fix issue with repeated library panels',
    "82320": '[v10.3.x] [DOC] Update Pyroscope data source',
    "82350": '[v10.3.x] Alerting docs: update `<GRAFANA VERSION>` to `<GRAFANA_VERSION>`',
    "82356": '[v10.3.x] Update `make docs` procedure',
    "82400": '[v10.3.x] Changelog: Updated changelog for 10.3.3',
    "82402": 'Release: Bump version to 10.3.4',
    "82432": '[v10.3.x] Chore: Update grabpl to v3.0.50',
    "82438": '[v10.3.x] Add PagerDuty to the plugins list',
    "82445": '[v10.3.x] Docs: Add copy dashboard instructions',
    "82537": '[v10.3.x] Chore: Remove grafana-delivery references',
    "82561": '[v10.3.x] Area Build/Packaging: release process - remove image check for armhf rpm no longer being built',
    "82713": '[v10.3.x] Adding Grafana for Beginners video to doc',
    "82731": '[v10.3.x] Adding "Exploring logs, metrics, and traces with Grafana" video to docs',
    "82877": '[v10.3.x] TeamSync: Fix auth proxy docs on teamsync',
    "82902": "[v10.3.x] LibraryPanels/RBAC: Fix issue where folder scopes weren't being correctly inherited",
    "82930": '[v10.3.x] docs: angular plugins list rewrite',
    "82939": '[v10.3.x] Add video to variables _index.md',
    "83052": '[v10.3.x] Update `make docs` procedure',
    "83055": '[v10.3.x] Remove duplicate paragraph and wrap in note',
    "83105": '[v10.3.x] Docs: add information about filtering for annotations',
    "83141": 'Alerting docs: Fix migrating alert links',
    "83142": '[v10.3.x] Alerting docs: fixes oncall broken links',
    "83177": '[v10.3.x] OAuth: Improve domain validation',
    "83203": '[v10.3.x] AuthProxy: Invalidate previous cached item for user when changes are made to any header',
    "83213": 'Tempo: Add template variable interpolation for filters',
    "83244": '[v10.3.x] Docs: update import troubleshoot dashboards links',
    "83325": '[v10.3.x] remove oss from security config docs',
    "83405": '[v10.3.x] Annotations: Improve query performance when using dashboard filter',
    "83428": '[v10.3.x] Docs/grafana helm',
    "83484": 'Auth: Fix email verification bypass when using basic authentication',
    "83525": '[v10.3.x] Dashboards: Fixes issue where panels would not refresh if time range updated while in panel view mode',
    "83553": '[v10.3.x] Docs: Add missing visualizations to Grafana vizualization index page',
    "83596": '[v10.3.x] Elasticsearch: Fix adhoc filters not applied in frontend mode',
    "83612": '[v10.3.x] docs: link annotation queries video to documentation',
    "83680": '[v10.3.x] Update `make docs` procedure',
    "83683": '[v10.3.x] Fix typos',
    "83702": '[v10.3.x] Docs: fix config file info in upgrade guide',
    "83722": '[v10.3.x] CI: Bump `alpine` image version',
    "83725": '[v10.3.x] Chore: Improve domain validation for Google OAuth - Backport 83229 to v10.3.x',
    "83731": '[v10.3.x] Chore: Bumping go to 1.21.6',
    "83750": '[v10.3.x] LDAP: Fix LDAP users authenticated via auth proxy not being able to use LDAP active sync',
    "83790": '[v10.3.x] Fix: Cache busting of plugins module.js file',
    "83837": '[v10.3.x] alerting:clarify silence preview',
    "83936": '[v10.3.x] chore: bump Go to 1.21.8'
}

# Populate JSON data with different models
json_data(sample, doc_sample, "spacy_model")
input("==")
json_data(sample, doc_sample, "AAA")
input("===")
json_data(sample, doc_sample, "BBB")

# Calculate averages and ranks
calculate_average_scores()
'''