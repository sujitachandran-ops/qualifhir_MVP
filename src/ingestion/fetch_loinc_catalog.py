import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_loinc_catalog(
    query="respiratory",
    rows=500,
    output_file="resources/loinc/loinc_output.json",
    username="",
    password=""
):
    offset_value = 0
    loinc_data = {'Results' : []}
    while True:
        url = (
            "https://loinc.regenstrief.org/searchapi/loincs"
            f"?query={query}&rows={rows}&offset={offset_value}&sortorder=loinc_num"
        )

        response = requests.get(
            url,
            auth=(username, password),
            timeout=10,verify=False
        )
        # response.raise_for_status()

        loinc_data['Results'].extend(response.json()['Results'])
        returned_rows = response.json().get('ResponseSummary', {}).get('RowsReturned', 0)

        if returned_rows < rows:
            break

        offset_value += rows

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(loinc_data, f, indent=2)

    print(f"LOINC catalog saved to {output_file}")
    print(f"Length of the data stored is {len(loinc_data['Results'])}")

if __name__ == "__main__":
    fetch_loinc_catalog()
