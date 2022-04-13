import requests
from newsapi import NewsApiClient
from twilio.rest import Client

# ----------------------------------- @Made by SouthPoleTUX ----------------------------------- #
# About the tasks/obstacles of the program
"""
1. Pull in the Stock Price we're interested in - API to get the data
    * Pulling yesterday's closing price and pull closing price on the previous day compare and get difference (%)
    * If difference > 10 % we want ot know
2. Fetch some relevant new - API
    * reasoning - gets called when difference > 10%
3. SMS --> telling us what was the big fluctuation that happened and what is the relevant news
"""
# # we are accessing the date class and the today method - we can convert the date object to make comparisons
# DATE_TODAY = datetime.date.today()
# # how to get yesterday's date in python - timedelta() - it will subtract with the parameters
# DATE_YESTERDAY = DATE_TODAY - datetime.timedelta(days=1)

# ----------------------------------- TARGET COMPANY INFORMATION ----------------------------------- #
STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

# ----------------------------------- API KEYS ----------------------------------- #
# @ About environment variables
"""
The value you assign to a temporary environment variable only lasts until you close the terminal session.
This is useful for variables you need to use for one session only or to avoid typing the same value multiple times.
"""

ALPHAVANTAGE_API_KEY = "API_KEY"
NEWSAPI_API_KEY = "API_KEY"
TWILIO_ACCOUNT_SID = "SID"
TWILIO_AUTH_TOKEN = "TOKEN"

# ----------------------------------- API ENDPOINTS - WHERE WE FETCH DATA ----------------------------------- #
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

# @Alpha vantage provides enterprise-grade financial market data through a set of powerful and developer-friendly apis
# ----------------------------------- GET DATA FROM ALPHAVANTAGE----------------------------------- #
# About functions of Alphavantage and question
"""
TIME_SERIES_DAILY --> returns raw (as-traded) daily time seires (data, daily open, daily high, daily low ...) 

Queston: When does the Stock market close?
The New York Stock Exchange (NYSE) and the Nasdaq Stock Market in the United States trade regularly 
from 9:30 a.m. to 4 p.m. ET, with the first trade in the morning creating the opening price for a stock and the final 
trade at 4 p.m. providing the day's closing price.
"""

url = "https://www.alphavantage.co/query"
# About @params for request to api
"""
function -- the time series of your choice
symbol -- the name fo the equity of your choice  
outputsize --> default=compact == only the latest 100 data points 
datatype --> default=json 
apikey == demo 
"""
params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": ALPHAVANTAGE_API_KEY
}
response = requests.get(url=url, params=params)
response.raise_for_status()
# the metadata described what we told the api --> tesla symbol and daily price
# I only want the time series
data = response.json()["Time Series (Daily)"]

# we can an online json format viewer to get a better view of the present data - we only want the data of yesterday yet,
# so we only want the closing prices and the dates - key = date and value ["close"]
# so we're filtering only the date and the close price by doing list comprehension

# ----------------------------------- FILTERING ALPHAVANTAGE DATA ----------------------------------- #
# we only want the values of the dates (date: 23:12 ... values = (4. close --> close price)
data_list = [value for (key, value) in data.items()]

# last day closing price: - [n] gives the counts of days before so index 0 would be the last day (yesterday)
# but we're assuming that we cannot get stock data (close price) of the current day only from yesterday
# the last prices
yesterday_data = data_list[0]
yesterday_closing_price = yesterday_data["4. close"]

day_before_yesterday_data = data_list[1]
day_before_yesterday_closing_price = day_before_yesterday_data["4. close"]

print(yesterday_closing_price)
print(day_before_yesterday_closing_price)

# @About percentage change in stock price
"""
Percentage change in stock price - it a own metric 
    * than look at how much the stock changed in price purely in dollars per share 
    * how--> subtract the old price from the new price = new  - old = ∆if pos --> price increase else decreased
        # lets say old price = p1 and new price = p2
        formula 100 * (new price - old price) / old price 
"""

difference = (float(yesterday_closing_price) -
              float(day_before_yesterday_closing_price))
print(difference)
# check whether stock had pos or neg increase
up_down = "🔺" if difference > 0 else "🔻"
# please round one decimal point or in other words to digits in total
diff_percent = round(
    (difference / float(day_before_yesterday_closing_price) * 100), 2)
print(diff_percent)

if abs(diff_percent > 5):
    # ----------------------------------- GET DATA FROM NEWSAPI----------------------------------- #
    # We have to use the unofficial python client library (pip) to integrate news api into python application to
    # make http requests directly - (btw by default pip command installs
    # the packages globally[available for all the users# in the system]

    # # STEP 2: https://newsapi.org/
    # Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.

    # Init the client with api key
    newsapi = NewsApiClient(api_key=NEWSAPI_API_KEY)

    # About @Endpoints
    """
    Endpoints -> an instance of NewsApiClient has three instance methods corresponding(dazugehoren)
    to three News Api endpoints
    
    *Everything /v2/everything - search every aticle published by over 80k different sources large and small in the last
        4 years --> ideal for news analysis and article discovery
    *Top headlines /v2/top-headlines --> returns breaking news headliens for countries, categories, and single published
        --> ideal for used with news tickers or anywhere : Usage of up-to-date news headlines
    *Sources /v2/top-headlines/sources --> returns information (including name, description, and category about the most
        notable sources available for obtaining top headlines from
    """

    # /v2/top-headlines
    # About the possible params of @top-headlines https://newsapi.org/docs/endpoints/top-headlines
    """
    PARAMETERS:
    q=keyword or a phrase to search for
    sources= use /top-headlines/sources  (comma-separated string of identifiers for the news sources or blogs
    category= possible, business, entertainment, gerneal, health, science, sports, technology 
        (cannot mix with sources para)
    language=
    country= 2 Letter format of IOS 316601 code of the country you want to get headlines for
    pageSize (int) = number of results to return per page (request) 20 default 100 max
    page (int) --> = to page through the results
    """
    # condition abs_dif_percentage > 5
    # @top headlines
    # top_headlines = newsapi.get_top_headlines(
    #     q="Tesla",
    #     category="business",
    #     country="us",
    # )
    # fetch data only articles no metadata
    all_articles = newsapi.get_everything(
        q="Tesla",
        # articles more closely related to q come first
        sort_by="relevancy",
    )["articles"]
    # filter the first articles headline and description to send later as sms
    three_articles = all_articles[:3]
    formatted_articles = [f"{STOCK_NAME}: {up_down}{diff_percent}%\nHeadline: {article['title']}: \n"
                          f"Brief:{article['description']}" for article in three_articles]
    # initialize client of Twilio
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    # we have 3 headline and description tuples, so we have three messages
    # title for message
    for article in formatted_articles:
        client.messages.create(
            body=article,
            from_="+NUMBER",
            to="+NUMBER"
        )
