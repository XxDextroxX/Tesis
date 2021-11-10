import tweepy
import os
import json

from os.path import exists

class StreamListener(tweepy.Stream):

    def __init__(self):
        
        
        self.path = "./tweets_streaming.json"
        self.should_create_file = False # if the json file should be created or not
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
                self.save_json(status._json)
            except Exception as e:
                print(e)

    def save_json(self, json_data):
        # If the file doesn't exist then I should write the
        # json structure.
        if not exists(self.path):
            self.should_create_file = True

        with open(self.path, "a+", encoding = "utf-8") as f:
            
            # [f] is a reference
            self.delete_last_line(f)

            # What you wanna write
            content = ('[\n' if self.should_create_file else ',') + f"{json.dumps(json_data)}\n]"

            if self.should_create_file:
                self.should_create_file = False

            f.write(content) # replacing the last line
            f.flush() # ensure file will be full writed before being readed again
            f.close() # closing the file


    # the [file] should be a reference
    def delete_last_line(self, file):
        # Move the pointer (similar to a cursor in a text editor) to the end of the file
        file.seek(0, os.SEEK_END)

        # This code means the following code skips the very last character in the file -
        # i.e. in the case the last line is null we delete the last line
        # and the penultimate one
        pos = file.tell() - 1

        # Read each character in the file one at a time from the penultimate
        # character going backwards, searching for a newline character
        # If we find a new line, exit the search
        while pos > 0 and file.read(1) != "\n":
            pos -= 1
            file.seek(pos, os.SEEK_SET)

        # So long as we're not at the start of the file, delete all the characters ahead
        # of this position
        if pos > 0:
            file.seek(pos, os.SEEK_SET)
            file.truncate()


    def on_error(self, status_code):
        # status code 420 means Tweetir has blocked the API key due to api call limit
        # and if that happens then connection should be sutted off
        if status_code == 420:
            return False

