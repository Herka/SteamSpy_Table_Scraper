import json
from robobrowser import RoboBrowser
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import simplejson
from login_data import account





def gettable_func(soup):

    ########
    #Scrape the OwnersTable from the raw Soup String
    #Parse the JSON table and turn it into an dataframe
    owner_table = str(soup.findAll("div", {"id": "tab-sales"}))
    owner_table = str(BeautifulSoup(owner_table, "lxml").contents)
    owner_table = "{%s}" % (owner_table.split("{", 1)[1].split("}")[0])
    owner_table = owner_table.replace("\"\"", "\"a\"").replace(", ,", ", 0 ,")
    owner_table = owner_table.replace("\\r", "").replace("\\n", "").replace("\\", "")
    owner_table = simplejson.loads(owner_table)
    df = pd.DataFrame(owner_table["values"], columns=["date", "owners", "col3", "event", "url"])
    df["date"] = df["date"].apply(lambda x: pd.to_datetime(datetime.datetime.fromtimestamp(x / 1000).strftime("%m.%d.%Y")))

    #####
    #Same for the Price at any given da
    price_table = str(soup.findAll("div", {"id": "tab-sales"}))
    price_table = str(BeautifulSoup(price_table, "lxml").contents)
    price_table = "{%s}" % (price_table.rsplit("{", 1)[1].split("}")[0]).replace(",,", ",").replace("#ffffff", "0.00")
    price_table = price_table.replace("\\r", "").replace("\\n", "").replace("\\", "")

    price_table = json.loads(price_table)
    price = pd.DataFrame(price_table["values"], columns=["date", "price", "col3", ])
    price["date"] = price["date"].apply(lambda x: pd.to_datetime(datetime.datetime.fromtimestamp(x / 1000).strftime("%m.%d.%Y")))


    ####
    #Changes
    changes_table = str(soup.findAll("div", {"id": "tab-changes"}))
    changes_table = str(BeautifulSoup(changes_table, "lxml").contents)
    changes_table = "{%s}" % (changes_table.split("{", 1)[1].split("}")[0])
    changes_table = changes_table.replace("\"\"", "\"a\"").replace(", ,", ", 0 ,")
    changes_table = changes_table.replace("\\r", "").replace("\\n", "").replace("\\", "")
    changes_table = simplejson.loads(changes_table)

    changes = pd.DataFrame(changes_table["values"], columns=["date", "changes", "col3", "event", "url"])
    changes["date"] = changes["date"].apply(lambda x: pd.to_datetime(datetime.datetime.fromtimestamp(x / 1000).strftime("%m.%d.%Y")))

    ######
    #Merge the three tables
    df = pd.merge(df, changes[["date", "changes"]], left_on="date", right_on="date")
    df = pd.merge(df, price[["date", "price"]], left_on="date", right_on="date")


    df.index = df["date"]
    return df[["owners", "changes", "price", "col3", "event", "url"]]





def steamspy_login(Login, PW , gameID):
    browser = RoboBrowser(history=True,
                          user_agent='Chrome/23.0.1271.64')
    acc_pwd = {"username": Login, "password": PW, "checkbox": 1}
    login_url = "http://steamspy.com/login/"
    browser.open(login_url)
    form = browser.get_form(id='login_form')
    form["username"].value = Login
    form["password"].value = PW
    browser.submit_form(form)

    URL = "http://steamspy.com/app/%s" % gameID
    browser.open(URL)
    webpage = str(browser.parsed)
    soup = BeautifulSoup(webpage, "lxml")
    return soup



def table_scraper(gameID):
        #Log into your account
        Login, PW  = account()
        webcontent = steamspy_login(Login, PW, gameID )

        df = gettable_func(webcontent)

        return df


