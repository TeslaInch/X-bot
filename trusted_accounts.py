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

#im using this instead of using the github repo, cause githubusercontent.com most times doesnt load up or takes alot of time to do so.
