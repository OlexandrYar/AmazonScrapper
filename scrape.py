import json
import time
import re
from bs4 import BeautifulSoup
import requests
import lxml
from concurrent.futures import ThreadPoolExecutor


def extractPrice(page):
    """
    Try multiple known Amazon price selectors in order of specificity.
    Returns the price string or "None" if nothing is found.
    """

    # Strategy 1: Look for the main "a-price" span (used on most modern layouts).
    # We target ones that are NOT struck-through (data-a-strike = "true").
    for price_span in page.select("span.a-price:not([data-a-strike]) .a-offscreen"):
        text = price_span.get_text(strip=True)
        if text:
            cleaned = re.sub(r'[^\d.,]', '', text)
            if cleaned:
                return cleaned

    # Strategy 2: Whole + fraction spans (original approach, but page-wide).
    whole = page.find("span", class_="a-price-whole")
    fraction = page.find("span", class_="a-price-fraction")
    if whole and fraction:
        return whole.get_text(strip=True) + fraction.get_text(strip=True)

    # Strategy 3: Various legacy / regional ID-based price holders.
    for selector_id in [
        "priceblock_ourprice",
        "priceblock_dealprice",
        "priceblock_saleprice",
        "tp_price_block_total_price_ww",
        "price",
    ]:
        el = page.find(id=selector_id)
        if el:
            text = el.get_text(strip=True)
            cleaned = re.sub(r'[^\d.,]', '', text)
            if cleaned:
                return cleaned

    # Strategy 4: "a-box-group" container (original code's method, as fallback).
    box = page.find("div", class_="a-box-group")
    if box:
        whole = box.find("span", class_="a-price-whole")
        fraction = box.find("span", class_="a-price-fraction")
        if whole and fraction:
            return whole.get_text(strip=True) + fraction.get_text(strip=True)

    # Strategy 5: corePriceDisplay (newer layout on some locales).
    core = page.find("div", id="corePriceDisplay_desktop_feature_div")
    if core:
        price_span = core.find("span", class_="a-offscreen")
        if price_span:
            cleaned = re.sub(r'[^\d.,]', '', price_span.get_text(strip=True))
            if cleaned:
                return cleaned

    return "None"


def priceAnotherCountry(session, domainEnding, asin):
    countryUrl = f'https://www.amazon.{domainEnding}/dp/{asin}'
    try:
        countryResult = session.get(countryUrl, timeout=10)
        countryPage = BeautifulSoup(countryResult.content, "lxml")
        return extractPrice(countryPage)
    except Exception:
        return "None"


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

    while pagenum <= pageLimit:
        url = f'https://www.amazon.ie/s?k={searchrequest}&page={pagenum}'
        result = session.get(url)
        page = BeautifulSoup(result.content, "lxml")
        allProducts = page.find_all("div", role="listitem")

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

                try:
                    link = product.find("a")["href"]
                except (TypeError, KeyError):
                    continue

                # Skip empty or whitespace-only hrefs
                if not link or not link.strip():
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