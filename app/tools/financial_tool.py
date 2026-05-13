import requests
from bs4 import BeautifulSoup


FINANCIAL_SOURCES = {
    "stocks": {
        "url": "https://finance.yahoo.com/markets/stocks/most-active/",
        "description": "Most active US stocks and market movers"
    },

    "crypto": {
        "url": "https://finance.yahoo.com/markets/crypto/all/",
        "description": "Cryptocurrency market trends including Bitcoin and Ethereum"
    },

    "currencies": {
        "url": "https://finance.yahoo.com/markets/currencies/",
        "description": "Forex and global currency exchange trends"
    }
}


def fetch_financial_page(url):

    try:

        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=10
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove scripts/styles
        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator=" ")

        text = " ".join(text.split())

        return text[:8000]

    except Exception as e:

        return f"Error fetching data: {str(e)}"


def financial_data_tool(query):

    query_lower = query.lower()

    if any(word in query_lower for word in [
        "stock",
        "stocks",
        "market",
        "nasdaq",
        "dow"
    ]):

        source_type = "stocks"

    elif any(word in query_lower for word in [
        "crypto",
        "bitcoin",
        "ethereum",
        "btc",
        "eth"
    ]):

        source_type = "crypto"

    else:

        source_type = "currencies"

    source_info = FINANCIAL_SOURCES[source_type]

    data = fetch_financial_page(source_info["url"])

    return f"""
    Financial Category:
    {source_type}

    Source Description:
    {source_info["description"]}

    Source URL:
    {source_info["url"]}

    Retrieved Financial Data:
    {data}
    """