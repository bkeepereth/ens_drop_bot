# ens_drop_bot

Special Thanks to @drakedanner for the inspiring this project.

## Notes

The bot will collect 99 tweets from the recent search Twitter Endpoint.<br>
The bot will parse and process each tweet from the response object. <br>
Each new tweet that comes in is checked against the mongodb cache, to check if it is a duplicate.<br>
If it is, the tweet is discarded.<br>
Otherwise, the tweet will be shipped to the Discord channel and logged in the cache.<br><br>
Repeat....</br>

## Future Improvements

The bot can become truly self-healing by adding a "groomer" process to the mongodb.
This process will clear out any entries older than 24-48 hours.

## Configuration

The bot relies on the Twitter API.<br>
The BEARER_TOKEN field must be present for the bot to function.<br>
A bearer token can be obtained by signing up for a Twitter Developer Account (FREE).<br>

DS_TOKEN refers to the Discord Bot Token used for auth.<br>
CHANNEL_ID refers to the Channel Id that the bot will send messages to.<br>

Lastly, the bot stores the tweet data in a mongodb cache.<br>
My mongo configuration is named 'ens_drop_daily' for the database and 'tweet_24hr' for the collection.<br>

## Usage
./ens_bot.py -c [config]

## EX: 
./ens_bot.py -c ../etc/config.xml

<p align="center" width="50%">
   <img src="work/ens_bot_test_run1.png">  
</p>
