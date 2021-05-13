import os
from pathlib import Path
import tweepy
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import cryptocompare


def twitter_authenticate(api_key, api_secret_key, acc_token, acc_secret_token):
    """ Authenticate to Twitter API"""
    auth_handler = tweepy.OAuthHandler(api_key, api_secret_key)
    auth_handler.set_access_token(acc_token, acc_secret_token)

    twitter_api = tweepy.API(auth_handler)

    try:
        twitter_api.verify_credentials()
        print("Authentication OK")
    except tweepy.TweepError:
        print("Error during authentication")
        raise ConnectionError("Could not connect to the Twitter API.")
    return auth_handler, twitter_api


def load_chrome_driver():
    options = Options()

    options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')

    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--remote-debugging-port=9222')

    return webdriver.Chrome(executable_path=str(os.environ.get('CHROMEDRIVER_PATH')), options=options)


def get_soup(webdriver, url):
    try:
        if url is not None:
            webdriver.get(url)
        else:
            webdriver.refresh()
        sleep(5)
        webdriver.execute_script("window.scrollTo(0, 0);")
        sleep(5)
        webdriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(5)
        return BeautifulSoup(webdriver.page_source, parser='html.parser', features='lxml')
    except Exception as e:
        return


if __name__ == "__main__":
    # Authenticate to the Twitter API
    auth, api = twitter_authenticate(api_key="API_KEY",
                                     api_secret_key="API_SECRET_KEY",
                                     acc_token="ACCESS_TOKEN",
                                     acc_secret_token="ACCESS_TOKEN_SECRET")
    # Authenticate to the CryptoCompare API
    crypto_compare_key = "CRYTPOCOMPARE_KEY"
    cryptocompare.cryptocompare._set_api_key_parameter(crypto_compare_key)
    # change this to your own Chrome path (you could use a portable version too,
    # but you have to make sure your chromedriver.exe version matches with you Chrome version)
    # chrome_path = r"/app/.apt/usr/bin/google-chrome"
    # opts = Options()
    # opts.binary_location = chrome_path
    # make this path point to your chromedriver executable
    # chrome_driver_path = Path(os.getcwd()).joinpath("Selenium").joinpath("chromedriver.exe")
    driver = None
    # Scrape the stat page continuously (once every hour) and tweet the data
    selectors = [
        ("Exchange Volume",
         "#__next > section > div:nth-child(3) > div.StatsRow__StatsRowContainer-sc-8kudbj-0.cLYEnH > div:nth-child(4) > div.StatsBox__StatsBoxNumber-z4sjtw-4.dwMgWP"),
        ("Trading Fees",
         "#__next > section > div:nth-child(3) > div.StatsRow__StatsRowContainer-sc-8kudbj-0.cLYEnH > div:nth-child(2) > div.StatsBox__StatsBoxNumber-z4sjtw-4.dwMgWP"),
        ("ETH Collateral",
         "#__next > section > div:nth-child(1) > div:nth-child(6) > div:nth-child(1) > div.StatsBox__StatsBoxNumber-z4sjtw-4.dwMgWP"),
        ("BTC Collateral",
         "#__next > section > div:nth-child(1) > div:nth-child(6) > div:nth-child(2) > div.StatsBox__StatsBoxNumber-z4sjtw-4.dwMgWP"),
        ("Amount of SNX staked",
         "#__next > section > div:nth-child(1) > div:nth-child(4) > div:nth-child(1) > div.StatsBox__StatsBoxNumber-z4sjtw-4.gGHOuN"),
        ("SNX Market Cap",
         "#__next > section > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > div.StatsBox__StatsBoxNumber-z4sjtw-4.gGHOuN")
    ]
    # Where we will hold the numbers
    data = []
    try:
        # Instantiate webdriver
        driver = load_chrome_driver()
        while True:
            data.clear()
            try:
                soup = get_soup(webdriver=driver, url=r"https://stats.synthetix.io/")
                url = None
                # Get the 24h exchange volume
                for i, selector in enumerate(selectors):
                    data.append((selector[0], soup.select(selector[1])[0].text))
                # convert the collateral and sum them up to get total value locked
                conversions = cryptocompare.get_price(["ETH", "BTC"], "USD")
                print(conversions)
                data.append(("Total value locked",
                             float(data[2][1].replace(',', '')) * conversions['ETH']['USD'] +
                             float(data[3][1].replace(',', '')) * conversions['BTC']['USD']))
                # Remove the collateral from the data (we only needed them for summing)
                data.pop(2)
                data.pop(2)
                # Calculate amount of SNX staked as a percentage of the total available
                staked_conv = float(str(data[-3][1]).split('.')[0].lstrip('$').replace(',', ''))
                total_conv = float(str(data[-2][1]).split('.')[0].lstrip('$').replace(',', ''))
                staked_percentage = (staked_conv / total_conv) * 100
                tweet_content = """Synthetix Trading Info\n"""
                for name, value in data:
                    # Remove commas from the number that contain them (this is because we have number that look like
                    # float and other that are formatted already. Making them all the same prevents weird special cases
                    # for the formatting done after)
                    amount = int(str(value).split('.')[0].lstrip('$').replace(',', ''))
                    if name == "Amount of SNX staked":
                        tweet_content += f"{name} : ${amount:,} ({staked_percentage:.2f}% of total)\n"
                    else:
                        tweet_content += f"{name} : ${amount:,}\n"
                tweet_content += "💰💰💰💰💰"
                print("Tweeting : \n" + tweet_content)
                print(f"Length of message : {len(tweet_content)}")
                api.update_status(tweet_content)
                sleep(3600)
            except Exception as e:
                break
    finally:
        print("Quitting...")
        if driver is not None:
            driver.quit()
        print("Goodbye :)")
