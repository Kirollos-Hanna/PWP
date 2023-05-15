# This script retrieves data from the API's hypermedia and transfers it to YAML format for openAPI
# Remember to launch flask before running this script: FLASK_APP=productsapi flask run

import requests
import yaml
import os.path

SERVER_ADDR = "http://localhost:5000/api"
DOC_ROOT = os.getcwd()
DOC_TEMPLATE = {
    "responses": {
        "200": {
            "content": {
                "application/vnd.mason+json": {
                    "example": {}
                }
            }
        }
    }
}

# This is needed for the authentication. Paste the token after the "Bearer".
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODQxNzkzMDgsImlhdCI6MTY4NDA5Mjg0OCwic3ViIjoia2FsYW1pZXMifQ.IXyWjSL9i5b6bXOvq3hG2txUNc_-0axzwZWf9yTyr_Q",
    "Content-Type": "application/json"
}

# After 'SERVER_ADDR +' insert the API's endpoint you want to use
resp_json = requests.get(SERVER_ADDR + "/categories/Books/", headers=headers).json()
DOC_TEMPLATE["responses"]["200"]["content"]["application/vnd.mason+json"]["example"] = resp_json
# Insert the filename you want to use after 'DOC_ROOT,'
with open(os.path.join(DOC_ROOT, "get.yml"), "w") as target:
    target.write(yaml.dump(resp_json, default_flow_style=False))
