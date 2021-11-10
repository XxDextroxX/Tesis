import tweepy

class StreamListener(tweepy.Stream):

    def __init__(self):
        
        self.consumer_key = "HRnrbF20nFjNBabu6W0d62dTa" # twitter app key
        self.consumer_secret = "1ZXn0mQbmw3AepGhMxTfSgybzB7KblHDWNjzEPe5iBZn1LVTf3" # twitter app secret
        self.access_token = "908144452723773440-MBkl0CRLu37lsz8ygCTkzp4dwZ6gxuY" # twitter key
        self.access_token_secret = "rZMpZ2QXCsfeoUfgKj7mtsZRJO1Bp1mLTjwuDVZafY9VY" # twitter secret
        
        super().__init__(
            self.consumer_key, self.consumer_secret, 
            self.access_token, self.access_token_secret
        )

    def on_status(self, status):
        if not hasattr(status, "retweeted_status"):
            try:
                print(status._json)
                # print(status.extended_tweet)
            except:
                print("Avoiding retweet")
            

    def on_error(self, status_code):
        # status code 420 means Tweetir has blocked the API key due to api call limit
        # and if that happens then connection should be sutted off
        if status_code == 420:
            return False

