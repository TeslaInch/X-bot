#logic to post the reply to the mention
def post_reply(trigger_tweet_id, report, trusted, client):
    trust_str = "✅ TRUSTED by network" if trusted else "⚠️ NOT TRUSTED by network"
    reply_text = f"{report}\n{trust_str}"
    client.create_tweet(text=reply_text, in_reply_to_tweet_id=trigger_tweet_id)
