import requests
import json
import pickle

import config

r = requests.get(config.URL, auth=(config.USERNAME, config.PASSWORD))

if r.status_code == 200:
    text = r.text
    json_obj = json.loads(text)

    schema = json_obj["schema"]
    data = json_obj["data"]

    for rind, row in enumerate(data):
        for cind, elem in enumerate(row):
            if cind>1 and elem!=None:
                row[cind] = float(elem)

        data[rind] = row

    with open(config.SCHEMA_FILE, "wb") as file:
        pickle.dump(schema, file)

    with open(config.DATA_FILE, "wb") as file:
        pickle.dump(data, file)

else:
    print("Status Code:", r.status_code)