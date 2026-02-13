def scrape():
    api_url = "https://www.thomann.it/solrsearch/select"

    params = {
        "q": "Squier Affinity Telecaster",
        "rows": 100,
        "wt": "json"
    }

    r = requests.get(api_url, params=params, headers=HEADERS)
    data = r.json()

    regular = []
    bstock = []

    for doc in data["response"]["docs"]:
        name = doc.get("title", "")
        price = doc.get("price")

        if not name or not price:
            continue

        try:
            value = float(price)
        except:
            continue

        if 180 <= value <= 250:
            link = "https://www.thomann.it/" + doc.get("url", "")

            entry = {
                "Name": name,
                "Price": value,
                "Link": link
            }

            if "B-Stock" in name:
                bstock.append(entry)
            else:
                regular.append(entry)

    return pd.DataFrame(regular), pd.DataFrame(bstock)


