import tweepy
import os
import time
from dotenv import load_dotenv
from analyzer import analyze_account
from trust_check import is_trusted_by_network
from replier import post_reply
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)  # See Tweepy info like rate limits

client = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
    wait_on_rate_limit=True
)

TRIGGER_PHRASE = "riddle me this"

last_seen_id = None  # Track the most recent tweet the bot has handled

def process_mentions():
    global last_seen_id
    bot_user = client.get_me().data

    response = client.get_users_mentions(
        id=bot_user.id,
        expansions=["referenced_tweets.id.author_id"],
        tweet_fields=["referenced_tweets"]
    )

    if not response.data:
        return  # No new mentions

    for tweet in reversed(response.data):  # Process from oldest to newest
        if last_seen_id and tweet.id <= last_seen_id:
            continue  # Skip already processed tweets

        if TRIGGER_PHRASE in tweet.text.lower():
            try:
                referenced = tweet.referenced_tweets[0] if tweet.referenced_tweets else None

                if referenced:
                    if referenced.type == "quoted":
                        print(f"Tweet {tweet.id} is a quote. Analyzing the quoter: @{tweet.author_id}")
                        original_author_id = tweet.author_id  # The person quoting the tweet
                    elif referenced.type == "replied_to":
                        print(f"Tweet {tweet.id} is a reply. Analyzing the original author.")
                        replied_tweet = client.get_tweet(referenced.id, expansions="author_id")
                        original_author_id = replied_tweet.includes['users'][0].id
                    else:
                        print(f"Tweet {tweet.id} has unknown reference type. Skipping.")
                        continue
                else:
                    print(f"Tweet {tweet.id} does not reference another tweet. Skipping.")
                    continue

                report = analyze_account(original_author_id, client)
                trust = is_trusted_by_network(original_author_id, client)
                post_reply(tweet.id, report, trust, client)

            except Exception as e:
                print(f"Error processing tweet {tweet.id}: {e}")

        last_seen_id = tweet.id

if __name__ == "__main__":
    bot_info = client.get_me().data
    print(f"🤖 Bot is running as: @{bot_info.username}")
    while True:
        try:
            process_mentions()
        except Exception as e:
            print(f"Unexpected error: {e}")
        time.sleep(60)  # Wait 60 seconds before checking again



