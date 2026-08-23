import requests
from concurrent.futures import ThreadPoolExecutor

ACCOUNT_ID=1
WITHDRAW_AMOUNT=100
URL=f"http://127.0.0.1:8000/accounts/{ACCOUNT_ID}/withdraw"

def withdraw():
    response = requests.post(URL, json={"amount": WITHDRAW_AMOUNT})
    return response.status_code, response.json()

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(lambda _: withdraw(), range(10)))

for result in results:
    print(result)