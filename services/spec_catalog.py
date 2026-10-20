import requests
from bs4 import BeautifulSoup


def get_series_specs(series):
    """
    Discover specification folders available in a
    3GPP specification series.

    Example:
        series = "38"

    Expected results include:
        38.101
        38.104
        38.211
        38.212
        38.213
        38.214
        38.321
        38.331
        ...
    """

    url = f"https://www.3gpp.org/ftp/Specs/archive/{series}_series/"

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        specs = []

        for link in soup.find_all("a"):
            text = link.get_text(strip=True)

            if text.startswith(f"{series}."):
                specs.append(text.rstrip("/"))

        return sorted(set(specs))

    except requests.RequestException as error:
        print("Error accessing 3GPP:", error)
        return []
def get_spec_metadata(spec_number):
    """
    Retrieve basic metadata for a 3GPP specification.
    """

    url = (
        "https://portal.3gpp.org/desktopmodules/"
        "Specifications/SpecificationDetails.aspx"
    )

    params = {
        "specificationId": spec_number
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        return {
            "spec_number": spec_number,
            "page_title": soup.title.get_text(strip=True)
            if soup.title else None,
            "url": response.url,
        }

    except requests.RequestException as error:
        print("Metadata lookup error:", error)
        return None
def get_3gpp_catalog_page():
    """
    Download the official 3GPP specification catalogue page.
    """

    url = "https://portal.3gpp.org/Specifications.aspx"

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        return response.text

    except requests.RequestException as error:
        print("Error accessing 3GPP catalogue:", error)
        return None