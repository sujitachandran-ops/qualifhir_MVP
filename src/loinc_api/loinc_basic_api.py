import json
import requests

url = "https://loinc.regenstrief.org/searchapi/loincs?query=glucose&rows=500&sortorder=loinc_num"
username = ""
password = ""

try:
    response = requests.get(
        url,
        auth=(username, password),
        timeout=10
    )
    # response.raise_for_status()

    data = response.json()  # convert response to Python object

    # Write output to JSON file
    with open(r".\output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("JSON file created successfully: output.json")

except requests.exceptions.RequestException as e:
    print("API request failed:", e)
except json.JSONDecodeError:
    print("Response is not valid JSON")
