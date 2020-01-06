from flask import Flask
from flask_ask import Ask, statement, question, session
import bs4 as bs
import urllib.request
import requests
from lxml import html
from random import randint

app = Flask(__name__)
ask = Ask(app, "/Webhall")

username = ""
password = ""
email = "" 
phone = ""

def get_product_details(productID):
    try:
        url = "https://www.webhallen.com/se-sv/" + str(productID)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        url_read = urllib.request.urlopen(req).read()
        soup = bs.BeautifulSoup(url_read,'lxml')
        productprice = float(soup.find("span", id="product_price").get_text())
        productname = soup.find("h1", itemprop="name").get_text()
        canbuy = soup.find("a", whprodid= productID).get_text()
        pagehierarchy = soup.find("p", class_="page_hierarchy").find_all("a", string = True)
        if "Lägg i varukorgen" in canbuy:
            lista = [productID,productname,productprice,pagehierarchy[1].get_text(),pagehierarchy[2].get_text(),pagehierarchy[3].get_text()]
            msg = lista
        else:
            msg = [None,None,None,None,None]
    except:
        msg = [None,None,None,None,None]
    return(msg)

def log_in(session):
    try:
        url = 'https://www.webhallen.com/se-sv/login.php'
        result = session.get(url)
        payload = {"username":username, "password":password}
        temp = session.post(url, data=payload)
        msg = session.get("https://www.webhallen.com/se-sv/medlem/" + username + "/bestallningar")
        soup = bs.BeautifulSoup(msg.content,"lxml")
        level = soup.find("div", id="member-header-rankinfo-summary-current")
        print(level)
        if level is None:
            session = None
    except:
        session = None
    return(session)   

def add_product(productID,session):
    try:
        url = 'https://www.webhallen.com/add/' + str(productID)
        temp = session.post(url)
        msg = session.get("https://www.webhallen.com")
        soup = bs.BeautifulSoup(msg.content,"lxml")
        item = soup.find("div", class_="basketprod")
    except:
        item = None
    return(item)

def buy_products(session):
    try:
        url2 = "https://www.webhallen.com/kassan-steg2?shippingtype=on&fraktsatt=4:20&paymenttype=2&personal_email=" + email + "&personal_phone=" + phone + "&accept_kopvillkor=1&category=1"
        temp = session.get(url2)
        soup = bs.BeautifulSoup(temp.content,"lxml")
        order = soup.find("span", class_="order_number")
    except:
        order = None
    return(order)

def get_product:
    session = requests.session()
    temp = 0
    while True:
        item = get_product_details(randint(20000,30000))
        temp = temp + 1
        print(temp, item)
        if item[0] != None and item[2] < 500:
            break
    productID = item[0] #153974 #255326
    get_product_details(productID)
    session = log_in(session)
    return add_product(productID,session)
    #buy_products(session)

@app.route('/')
def homepage():
    return "Hi there, You want to order a random thing?"

@ask.launch
def start_skill():
    welcome_message = 'You want to order a random thing?'
    return question(welcome_message)

@ask.intent("YesIntent")
def share_headlines():
    product = get_product()
    headline_msg = 'You have order {}'.format(product)
    return statement(headline_msg)

@ask.intent("NoIntent")
def no_intent():
    bye_text = 'What do you want to do?'
    return statement(bye_text)
    
if __name__ == '__main__':
    app.run(debug=True)