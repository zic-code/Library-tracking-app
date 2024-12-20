import yfinance as yf


def get_historical_stock_price(symbol, year,month):

    """Gets the opening price for a specific year and month through Yahoo Finance."""
    stock = yf.Ticker(symbol)
    print(f"Debug: Function called with symbol={symbol}, year={year}, month={month}")
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month+1:02d}-01" if month < 12 else f"{year+1}-01-01"

    hist = stock.history(start=start_date, end=end_date, interval="1mo")
    if not hist.empty:
        return hist.iloc[0]["Open"]  # Opening price of the first day of the month
    return None