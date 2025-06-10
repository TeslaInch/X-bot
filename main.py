import tweepy
import os
import time
from dotenv import load_dotenv
from analyzer import analyze_account
from trust_check import is_trusted_by_network
from replier import post_reply
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)

client = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
    wait_on_rate_limit=True
)

TRIGGER_PHRASE = "riddle me this"
SEEN_FILE = "last_seen_id.txt"
CACHE = {}

# Last seen cache
LAST_SEEN_ID = None

def load_last_seen_id():
    global LAST_SEEN_ID
    try:
        with open(SEEN_FILE, "r") as f:
            LAST_SEEN_ID = int(f.read().strip())
    except:
        LAST_SEEN_ID = None

def save_last_seen_id(tweet_id):
    global LAST_SEEN_ID
    if tweet_id != LAST_SEEN_ID:
        with open(SEEN_FILE, "w") as f:
            f.write(str(tweet_id))
        LAST_SEEN_ID = tweet_id

def process_mentions():
    bot_user = client.get_me().data
    response = client.get_users_mentions(
        id=bot_user.id,
        since_id=LAST_SEEN_ID,
        expansions=["referenced_tweets.id.author_id", "author_id"],
        tweet_fields=["referenced_tweets", "created_at"],
        user_fields=["username"]
    )

    if not response.data:
        logging.info("No new mentions.")
        return

    users = {u.id: u for u in response.includes.get('users', [])}
    new_last_seen_id = LAST_SEEN_ID

    for tweet in reversed(response.data):
        if TRIGGER_PHRASE not in tweet.text.lower():
            continue

        try:
            original_author_id = None

            # Handle quotes and replies
            if tweet.referenced_tweets:
                ref = tweet.referenced_tweets[0]
                if ref.type == "quoted":
                    original_author_id = tweet.author_id  # Analyze who quoted
                    logging.info(f"🔁 Quote mention. Analyzing quoter @{users[original_author_id].username}")
                elif ref.type == "replied_to":
                    replied = client.get_tweet(ref.id, expansions="author_id", user_fields=["username"])
                    original_author_id = replied.includes['users'][0].id
                    logging.info(f"↩️ Reply mention. Analyzing replied-to user ID: {original_author_id}")

            if not original_author_id:
                logging.info(f"❌ Tweet {tweet.id} has no reference target. Skipping.")
                continue

            # Use cached data
            if original_author_id in CACHE:
                report, trust = CACHE[original_author_id]
                logging.info(f"✅ Using cache for user {original_author_id}")
            else:
                report = analyze_account(original_author_id, client)
                trust = is_trusted_by_network(original_author_id, client)
                CACHE[original_author_id] = (report, trust)

            # Post reply
            post_reply(tweet.id, report, trust, client)
            new_last_seen_id = max(new_last_seen_id or 0, tweet.id)

        except Exception as e:
            logging.error(f"🚫 Error handling tweet {tweet.id}: {e}")

    if new_last_seen_id:
        save_last_seen_id(new_last_seen_id)

if __name__ == "__main__":
    bot_user = client.get_me().data
    logging.info(f"🤖 Bot running as @{bot_user.username}")
    load_last_seen_id()

    while True:
        try:
            process_mentions()
        except Exception as e:
            logging.error(f"🔥 Fatal error: {e}")
        time.sleep(15)  # ⏱️ Lower delay = faster bot, just watch for rate limits
