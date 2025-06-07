from datetime import datetime
from textblob import TextBlob
from collections import Counter
import re
from trusted_accounts import fetch_trusted_accounts

TRUSTED_ACCOUNT_IDS = set(fetch_trusted_accounts())

def analyze_account(user_id, client):
    user = client.get_user(id=user_id, user_fields=["created_at", "description", "public_metrics", "protected"])
    
    if user.data.protected:
        return "⚠️ Account is private/protected; limited analysis possible."
    
    metrics = user.data.public_metrics

    # 1. Account Age
    age = (datetime.utcnow() - user.data.created_at).days

    # 2. Follower/Following Ratio
    ratio = metrics['followers_count'] / max(1, metrics['following_count'])

    # 3. Bio analysis
    bio = user.data.description or ""
    bio_length = len(bio)
    keyword_list = ["rug","BTC","CRYPTO","WEB3", "dev", "DAO", "NFT", "AI", "founder", "CEO"]
    bio_keywords = [kw for kw in keyword_list if kw.lower() in bio.lower()]

    # 4. Recent tweets analysis
    tweets = client.get_users_tweets(id=user_id, max_results=10, tweet_fields=["public_metrics"])
    tweets_data = tweets.data if tweets.data else []

    sentiment_scores = []
    all_words = []
    total_likes, total_retweets = 0, 0

    for tweet in tweets_data:
        text = tweet.text
        sentiment_scores.append(TextBlob(text).sentiment.polarity)
        all_words += re.findall(r'\w+', text.lower())
        metrics = tweet.public_metrics
        total_likes += metrics["like_count"]
        total_retweets += metrics["retweet_count"]

    avg_sentiment = sum(sentiment_scores) / max(1, len(sentiment_scores))
    avg_likes = total_likes / max(1, len(tweets_data))
    avg_retweets = total_retweets / max(1, len(tweets_data))
    common_words = ", ".join([w for w, _ in Counter(all_words).most_common(5)])

    # 5. Trust Network Check
    followers = client.get_users_followers(id=user_id, max_results=100).data or []
    follower_ids = {f.id for f in followers}
    trusted_overlap = follower_ids & TRUSTED_ACCOUNT_IDS
    trust_score = len(trusted_overlap)

    report = (
        f" Trust Report:\n"
        f"• Account Age: {age} days\n"
        f"• Follower Ratio: {ratio:.2f}\n"
        f"• Bio Length: {bio_length} chars\n"
        f"• Bio Keywords: {', '.join(bio_keywords) if bio_keywords else 'None'}\n"
        f"• Avg Likes: {avg_likes:.2f} | Retweets: {avg_retweets:.2f}\n"
        f"• Avg Sentiment: {avg_sentiment:.2f}\n"
        f"• Topics: {common_words}\n"
        f"• Trusted Follower Matches: {trust_score} ✅"
        
    )

    return report
