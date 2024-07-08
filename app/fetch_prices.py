from datetime import datetime, timedelta

import requests

API_BASE_URL = "https://west.albion-online-data.com/api/v2/stats"


def fetch_historical_prices(item_id, locations, quality, days=7, time_scale=24):
    """
    Fetch historical prices for a given item and locations.

    Parameters:
    - item_id: The item ID to fetch prices for.
    - locations: A list of location names.
    - quality: The quality of the item.
    - days: Number of days to fetch historical data for.
    - time_scale: The timescale in hours (1 for hourly, 24 for daily).

    Returns:
    - A dictionary with location as key and average price as value.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    url = f"{API_BASE_URL}/history/{item_id}.json?date={start_date.strftime('%Y-%m-%d')}&end_date={end_date.strftime('%Y-%m-%d')}&locations={','.join(locations)}&qualities={quality}&time-scale={time_scale}"

    response = requests.get(url)
    historical_data = response.json()

    averages = {}
    for entry in historical_data:
        location = entry['location']
        prices = [data['avg_price'] for data in entry['data']]

        if prices:
            avg_price = sum(prices) / len(prices)
        else:
            avg_price = None

        averages[location] = avg_price

    return averages
