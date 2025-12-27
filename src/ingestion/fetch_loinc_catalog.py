import json
import requests

def fetch_loinc_catalog(
    query="glucose",
    rows=500,
    output_file="resources/loinc/loinc_output.json",
    username=None,
    password=None
):
    url = (
        "https://loinc.regenstrief.org/searchapi/loincs"
        f"?query={query}&rows={rows}&sortorder=loinc_num"
    )

    response = requests.get(
        url,
        auth=(username, password),
        timeout=10
    )
    response.raise_for_status()

    data = response.json()

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"LOINC catalog saved to {output_file}")

if __name__ == "__main__":
    fetch_loinc_catalog()
