import json
import time
import re
from bs4 import BeautifulSoup
import requests
import lxml
from concurrent.futures import ThreadPoolExecutor

def priceAnotherCountry(session, domainEnding, asin):
    countryUrl = f'https://www.amazon.{domainEnding}/dp/{asin}'
    countryResult = session.get(countryUrl)
    countryPage = BeautifulSoup(countryResult.content, "lxml")

    try:
        innerBlock = countryPage.find("div", class_="a-box-group")
        price = innerBlock.find("span", class_="a-price-whole").text + innerBlock.find("span", class_="a-price-fraction").text
    except:
        price = "None"

    return price


def search(searchrequest):
    pagenum = 1
    sleepTime = 0
    pageLimit = 3
    workersNum = 20

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    session = requests.Session()
    session.headers.update(headers)

    productObject = {
        "title": "",
        "price_ie": "",
        "price_uk": "",
        "price_de": "",
        "image": "",
        "link_ie": "",
        "link_de": "",
        "link_uk": "",
        "asin": "",
    }
    resultsList = []

    # BUG 1 FIX: Removed the redundant initial request that was never used for
    # product extraction. The while loop now handles all page fetches.

    while pagenum <= pageLimit:
        url = f'https://www.amazon.ie/s?k={searchrequest}&page={pagenum}'
        result = session.get(url)
        page = BeautifulSoup(result.content, "lxml")
        allProducts = page.find_all("div", role="listitem")

        # BUG 2 FIX: Break if no products found (was only checked at top of
        # loop before, but the check was against stale data from the previous
        # iteration or the redundant initial fetch).
        if not allProducts:
            break

        with ThreadPoolExecutor(max_workers=workersNum) as executor:
            futures = []
            for product in allProducts:
                try:
                    innerText = product.find("h2", class_="a-size-base-plus a-spacing-none a-color-base a-text-normal")
                    title = innerText.find("span").text
                except:
                    title = "None"

                try:
                    price = product.find("span", class_="a-price-whole").text + product.find("span", class_="a-price-fraction").text
                except:
                    price = "None"

                try:
                    image = product.find("img", class_="s-image").attrs["src"]
                except:
                    image = "None"

                # BUG 3 FIX: The link lookup can fail if the product div has no
                # <a> tag or no href. Wrapped in try/except to avoid crashing.
                try:
                    link = product.find("a")["href"]
                except (TypeError, KeyError):
                    continue

                match = re.search(r'/dp/([A-Z0-9]{10})', link)

                newProductObject = productObject.copy()

                newProductObject["title"] = title
                newProductObject["price_ie"] = price
                newProductObject["image"] = image

                if match:
                    asin = match.group(1)
                    newProductObject["link_ie"] = "https://www.amazon.ie/dp/" + asin
                    newProductObject["link_de"] = "https://www.amazon.de/dp/" + asin
                    newProductObject["link_uk"] = "https://www.amazon.co.uk/dp/" + asin
                    newProductObject["asin"] = asin

                    futureDE = executor.submit(priceAnotherCountry, session, "de", asin)
                    futureUK = executor.submit(priceAnotherCountry, session, "co.uk", asin)
                    futures.append((newProductObject, futureDE, futureUK))
                else:
                    resultsList.append(newProductObject)

            for obj, futureDE, futureUK in futures:
                obj["price_de"] = futureDE.result()
                obj["price_uk"] = futureUK.result()
                resultsList.append(obj)

        time.sleep(sleepTime)
        pagenum += 1

    resultJSON = json.dumps(resultsList, indent=1)
    return resultJSON