# Synthetix-Twitter-Bot
A simple Twitter Bot to stay informed about Synthetix stats.

### EDIT  

Added timestamps (idea came from [spiyer99](https://github.com/spiyer99/synthetix_stats_twitter_bot)).  
Also decided to remove the market cap to be able to keep the total value stacked<br/>
in ETH and BTC (also from [spiver99](https://github.com/spiyer99/synthetix_stats_twitter_bot)).  
I did keep the total value staked (ETH+BTC) converted to USD with live rates.

As proof, here's a picture from my bot Tweeter account:  
![Proof](https://user-images.githubusercontent.com/13340366/118216281-3c271400-b441-11eb-8688-f4d5e5fa99ee.png)


TODOs:
- [X] Setup Twitter Dev account and app
- [X] Setup web scraper in Python
- [X] Run Twitter bot in Python along with the web scraper
- [X] Deploy to Heroku
- [X] Write a nice little guide

## Tutorial on how to use it
1. `git clone` this repo
2. Make a Python `venv`
3. Run `pip install requirement.txt` in the `venv` you've just created
4. Create an app in your Twitter developer account (https://developer.twitter.com/en)
5. Create an account on https://www.cryptocompare.com/ and get your API key
6. Fill in the bot.py file with your Twitter app, Cryptocompare API keys and Chrome path
7. Create App on Heroku
8. Go to the ***Settings*** tab of your app and add these to your ***Buildpacks***:
    1. heroku/python
    2. heroku/google-chrome
    3. heroku/chromedriver
9. Install Heroku CLI
10. Follow the instruction on the ***Deploy*** tab of your Heroku App
11. Before you push the repo to Heroku, run these two commands to make the environment
    variable available to the bot:
    1.`heroku config:set CHROMEDRIVER_PATH=/app/.chromedriver/bin/chromedriver`\
    2.`heroku config:set GOOGLE_CHROME_BIN=/app/.apt/usr/bin/google-chrome`
12. If your app is still not running for some reason, go and make sure that
    your worker is enabled in the ***Resources*** tab of your App
13. If it still does not start, run this command : `heroku ps:scale worker=1`
14. 🎉Enjoy🎉 :smiley:
