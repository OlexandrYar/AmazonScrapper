# Amazon Price Comparator

A Flask web application that lets users search for products and compare prices across Amazon Ireland, Germany, and the UK marketplaces.

## How It Works

1. User submits a search query on the home page
2. The app scrapes Amazon.ie for matching products (by ASIN)
3. Prices are concurrently fetched from Amazon.de and Amazon.co.uk using ThreadPoolExecutor
4. Results are displayed in a responsive grid; users can also download results as CSV

## Project Structure

```
.
├── app.py              # Flask application (routes + API)
├── scrape.py           # Amazon scraping logic
├── requirements.txt    # Python dependencies
├── static/
│   └── css/
│       └── styles.css  # Custom styles
└── templates/
    ├── index.html      # Home/search page
    └── products.html   # Results page with JS logic
```

## Tech Stack

- **Backend:** Python, Flask, BeautifulSoup4, lxml, requests
- **Frontend:** HTML, CSS, Bootstrap 5, vanilla JavaScript
- **Scraping:** concurrent.futures (ThreadPoolExecutor) for parallel price fetching

## Running the App

```bash
python app.py
```

Runs on `0.0.0.0:5000`.

## Deployment

Configured for autoscale deployment using gunicorn:
```
gunicorn --bind=0.0.0.0:5000 --reuse-port app:app
```
