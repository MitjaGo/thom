import requests
import pandas as pd

HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape():
    """
    Scrape Thomann Squier Affinity Telecasters using Solr JSON API.
    Separates Regular and B-Stock based on 'condition' field.
    Returns: regular_df, bstock_df
    """
    api_url = "https://www.thomann.it/solrsearch/select"

    # Solr query parameters
    params = {
        "q": "Affinity Telecaster",  # search for Affinity Telecaster
        "fq": "manufacturer:Squier",  # filter manufacturer
        "rows": 100,                  # get up to 100 results
        "wt": "json"                  # JSON response
    }

    response = requests.get(api_url, params=params, headers=HEADERS)
    data = response.json()

    regular = []
    bstock = []

    for doc in data["response"]["docs"]:
        name = doc.get("title", "")
        price = doc.get("price")
        link = "https://www.thomann.it/" + doc.get("url", "")
        condition = doc.get("condition", "new")  # some have "B-Stock"

        if not name or not price:
            continue

        try:
            price_value = float(price)
        except:
            continue

        if 180 <= price_value <= 250:
            entry = {
                "Name": name,
                "Price": price_value,
                "Link": link
            }

            if condition.lower() in ["b-stock", "b stock", "used"]:
                bstock.append(entry)
            else:
                regular.append(entry)

    # Sort by price ascending
    regular_df = pd.DataFrame(regular).sort_values("Price")
    bstock_df = pd.DataFrame(bstock).sort_values("Price")

    return regular_df, bstock_df



