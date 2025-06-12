import requests
from fallback_accounts import TRUSTED_ACCOUNTS as FALLBACK_LIST

def fetch_trusted_accounts():
    url = "https://github.com/devsyrem/turst-list.git"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return FALLBACK_LIST

#The function above returns the trusted accounts list, i set up a fallback list just incase github fails to fetch it in real time.