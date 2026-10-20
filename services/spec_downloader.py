import requests
import zipfile
from pathlib import Path


BASE_URL = "https://www.3gpp.org/ftp/Specs/archive"


def download_spec(spec_number, version, filename):
    """
    Download a 3GPP specification ZIP and extract it locally.
    """

    series = spec_number.split(".")[0]

    url = (
        f"{BASE_URL}/"
        f"{series}_series/"
        f"{spec_number}/"
        f"{filename}"
    )

    destination = (
        Path("data/specs")
        / spec_number
        / version
    )

    destination.mkdir(
        parents=True,
        exist_ok=True
    )

    zip_path = destination / filename

    print("Downloading:", url)

    response = requests.get(
        url,
        timeout=60
    )

    response.raise_for_status()

    with open(zip_path, "wb") as file:
        file.write(response.content)

    print("Downloaded:", zip_path)

    with zipfile.ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(destination)

    print("Extracted to:", destination)

    return destination
def build_spec_url(spec_number, filename):
    series = spec_number.split(".")[0]

    return (
        f"{BASE_URL}/"
        f"{series}_series/"
        f"{spec_number}/"
        f"{filename}"
    )