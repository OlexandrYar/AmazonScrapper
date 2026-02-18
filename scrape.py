import time
import re
import random
from bs4 import BeautifulSoup
import requests
import  lxml



searchrequest = "RTX 5050"
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


#get products
while allProducts != []:
    pagenum += 1
    url = f'https://www.amazon.ie/s?k={searchrequest}&page={pagenum}'
    result = session.get(url)
    page = BeautifulSoup(result.content, "lxml")
    allProducts = page.find_all("div", role="listitem")
    if allProducts != []:
        print("Page:" + str(pagenum))
    for product in allProducts:
        try:
            innerText = product.find("h2", class_="a-size-base-plus a-spacing-none a-color-base a-text-normal")
            title = innerText.find("span")

        except:
            print(product.find("h2", class_="a-size-base-plus a-spacing-none a-color-base a-text-normal"))

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

        print("Title: " + title.text)
        print("Price: " + price)
        print("Image: " + image)
        if match:
            asin = match.group(1)
            print("Link: " + "https://www.amazon.ie/dp/" + asin)
            print("ASIN: " + asin)
        print("---------------------------------------------")

    time.sleep(sleepTime)