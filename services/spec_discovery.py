import requests
from bs4 import BeautifulSoup
def detect_rat(question):
    """
    Detect which Radio Access Technology the user is asking about.

    Returns:
        "4G"
        "5G"
        "6G"
        None
    """

    question = question.lower()

    if "6g" in question:
        return "6G"

    if "5g" in question or "nr" in question:
        return "5G"

    if "4g" in question or "lte" in question:
        return "4G"

    return None
RAT_SPEC_SERIES = {
    "4G": ["36"],
    "5G": ["38"],
    "6G": []
}


def get_spec_series(rat):
    return RAT_SPEC_SERIES.get(rat, [])
def check_3gpp_connection():
    url = "https://www.3gpp.org/ftp/Specs/archive/"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return True

        return False

    except requests.RequestException:
        return False
def get_spec_versions(spec_number):
    series = spec_number.split(".")[0]

    url = (
        f"https://www.3gpp.org/ftp/Specs/archive/"
        f"{series}_series/{spec_number}/"
    )

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        versions = []

        for link in soup.find_all("a"):
            filename = link.get_text(strip=True)

            if filename.lower().endswith(".zip"):
                versions.append(filename)

        return versions

    except requests.RequestException as error:
        print("Error accessing 3GPP:", error)
        return []
def decode_3gpp_character(char):
    characters = "0123456789abcdefghijklmnopqrstuvwxyz"
    return characters.index(char.lower())


def decode_3gpp_version(filename):
    """
    Example:
    38321-j40.zip -> 19.4.0
    """

    version_code = filename.split("-")[1].split(".")[0]

    major = decode_3gpp_character(version_code[0])
    technical = decode_3gpp_character(version_code[1])
    editorial = decode_3gpp_character(version_code[2])

    return f"{major}.{technical}.{editorial}"