import datetime
import requests
from twilio.rest import Client
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_API_KEY = "[INSERT_STOCK_API_KEY]"
NEWS_API = "[INSERT_NEW_API_KEY]"
SENDER_NUMBER = '[INSERT_SENDER_NUMBER ]'
RECIPIENT_NUMBER = '[INSERT_RECIPIENT_NUMBER]'

"""The program is comparing prices of Tesla stock from yesterday and day before yesterday. If diference between prices increased or decreased about until 5% then program send sms to user """
# STOCK PRICES: https://www.alphavantage.co
# NEWS API: https://newsapi.org
# SEND MESSAGE: https://www.twilio.com/en-us


# Get yesterday from date
def get_yesterday(date):
    new_date = date - datetime.timedelta(days=1)
    return new_date


# Get data from api
def get_current_data_():
    url = 'https://www.alphavantage.co/query?'
    query_params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": STOCK,
        "apikey": STOCK_API_KEY
    }
    r = requests.get(url, params=query_params)
    r.raise_for_status()
    data = r.json()["Time Series (Daily)"]
    return data


# Get close price of the day
def get_close_price_for_day(date, data):
    date_str = str(date)
    close_price = float(data[date_str]['4. close'])
    return close_price


# Get difference between yesterday and day before yesterday
def get_difference_perc(yesterday_price, day_before_price):
    percentage = round((yesterday_price * 100) / day_before_price, 2)
    diff = round(percentage - 100.00, 2)
    return diff


# Get articles from Actual to date
def get_articles(date):
    # https://newsapi.org/v2/everything?q=tesla&from=2023-06-09&sortBy=publishedAt&apiKey=5a882fc2b2794b2d993cbd7142044dea
    query_params = {
        "q": COMPANY_NAME,
        "from": date,
        "language": "en",
        "sortBy": "publishedAt",
        "apiKey": NEWS_API
    }
    main_url = "https://newsapi.org/v2/everything?"

    # fetching data in json format
    res = requests.get(main_url, params=query_params)
    data = res.json()

    # getting all articles in a string article
    article = data["articles"]

    # empty list which will
    # contain 3 trending news
    results = [ (article[ar]["title"], article[ar]["description"]) for ar in range(3)]
    # for ar in range(3):
    #     f_ar = (article[ar]["title"], article[ar]["description"])
    #     results.append(f_ar)
    print(results)
    return results


# SEND MESSAGE
def send_message(articles, diff):
    difference = f"{STOCK}: "
    if diff < 0:
        difference += f"🔻{diff} %"
    else:
        difference += f"🔺{diff} %"
    account_sid = 'AC7ceb3d818413b972266d045cb9fe8bcf'
    auth_token = '7593d6254b4b22566e69ce0908148706'
    client = Client(account_sid, auth_token)
    for ar in articles:
        body = f"\n{difference}\n Headline: {ar[0]}\n Brief: {ar[1]}"
        message = client.messages.create(
            body=body,
            from_=SENDER_NUMBER,
            to=RECIPIENT_NUMBER
        )


def main():
    # ---------------------------DATES-----------------------------
    # ACTUAL DATE
    actual_date = datetime.date.today() - datetime.timedelta(days=1)
    # YESTERDAY
    yesterday = get_yesterday(date=actual_date)
    # DAY BEFORE YESTERDAY
    day_before_yesterday = get_yesterday(date=yesterday)

    # GET DATA FROM API
    data = get_current_data_()
    # GET CLOSE PRICE  FOR DAYS
    price_yesterday = get_close_price_for_day(date=yesterday, data=data)
    print(price_yesterday)
    price_day_before_yesterday = get_close_price_for_day(date=day_before_yesterday, data=data)
    print(price_day_before_yesterday)
    # DIFFERENCE BETWEEN PRICES
    diff = get_difference_perc(yesterday_price=price_yesterday, day_before_price=price_day_before_yesterday)

    # GET ARTICLE AND SEND SMS
    if abs(diff) <= 5:
        articles = get_articles(date=str(yesterday))
        send_message(articles=articles, diff=diff)


if __name__ == '__main__':
    main()
