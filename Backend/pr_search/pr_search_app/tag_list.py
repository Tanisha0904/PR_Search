
import requests


def version_key(version):
    version_number = version.lstrip("v")
    # Handle 'preview' versions by removing the '-preview' suffix for sorting
    if "preview" in version_number:
        version_number = version_number.split("-")[0]
    return tuple(map(int, version_number.split(".")))


def get_tag_list(owner, repo):
    # GitHub API endpoint for releases
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"

    tag_list = []

    # Make a GET request to the GitHub API
    response = requests.get(url)

    if response.status_code == 200:
        json_data = response.json()
        tag_list = [release["tag_name"] for release in json_data]
    else:
        print(
            f"Failed to fetch release information. Status code: {response.status_code}"
        )

    indexed_tag_list_dict = {}
    for i, x in enumerate(sorted(tag_list, key=version_key, reverse=True)):
        indexed_tag_list_dict[i] = x
    return indexed_tag_list_dict
