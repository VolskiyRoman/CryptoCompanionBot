import requests


def get_crypto_exchange_rate(symbol):
    url = f'https://api.coincap.io/v2/assets/{symbol}/'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        rate_usd_str = data.get('data', {}).get('priceUsd')

        try:
            rate_usd = float(rate_usd_str)

            if rate_usd is not None and rate_usd != 0:
                rate_reverse = 1 / rate_usd

                return rate_usd, rate_reverse
            else:
                return None, None
        except ValueError:
            print(f"Could not convert '{rate_usd_str}' to a float.")
            return None, None
    else:
        return None, None