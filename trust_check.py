#import the list of trusted accounts from fetch_trusted_accounts_module 
from trusted_accounts import fetch_trusted_accounts


TRUSTED_ACCOUNTS = set(fetch_trusted_accounts())

def is_trusted_by_network(user_id, client):
    user = client.get_user(id=user_id, user_fields=["protected"])
    if user.data.protected:
        # Private account — cannot check followers reliably
        return False

    followers_response = client.get_users_followers(id=user_id, max_results=1000)
    followers = followers_response.data or []

    count = sum(1 for f in followers if f.username.lower() in TRUSTED_ACCOUNTS)
    return count >= 2
#The function above gets the 1000 of the account's followers and compare them to the trusted list.
#if there are more than 2 present, it is trusted.