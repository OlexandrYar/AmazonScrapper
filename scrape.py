import json
import time
import re
import random
from bs4 import BeautifulSoup
import requests
import  lxml

def searchIE(searchrequest):

    pagenum = 0
    sleepTime = 0

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    session = requests.Session()
    session.headers.update(headers)

    url = f'https://www.amazon.ie/s?k={searchrequest}'
    result = session.get(url)
    page = BeautifulSoup(result.content, "lxml")
    allProducts = page.find_all("div", role="listitem")

    productObject = {
        "title": "",
        "price": "",
        "image": "",
        "link": "",
        "asin": "",
    }
    resultsList = []



    #get products
    while allProducts != []:
        pagenum += 1
        url = f'https://www.amazon.ie/s?k={searchrequest}&page={pagenum}'
        result = session.get(url)
        page = BeautifulSoup(result.content, "lxml")
        allProducts = page.find_all("div", role="listitem")
        for product in allProducts:
            try:
                innerText = product.find("h2", class_="a-size-base-plus a-spacing-none a-color-base a-text-normal")
                title = innerText.find("span").text

            except:
                title = "None"


            try:
                price = product.find("span", class_="a-price-whole").text + product.find("span",class_="a-price-fraction").text
            except:
                price = "None"

            try:
                image = product.find("img", class_="s-image").attrs["src"]
            except:
                image = "None"
            link = product.find("a")["href"]
            match = re.search(r'/dp/([A-Z0-9]{10})', link)

            newProductObject = productObject.copy()

            newProductObject["title"] = title
            newProductObject["price"] = price
            newProductObject["image"] = image

            if match:
                asin = match.group(1)
                newProductObject["link"] = "https://www.amazon.ie/dp/" + asin
                newProductObject["asin"] = asin

            resultsList.append(newProductObject)

        time.sleep(sleepTime)

    resultJSON = json.dumps(resultsList, indent=1)
    return resultJSON

print(searchIE("RTX 5070"))