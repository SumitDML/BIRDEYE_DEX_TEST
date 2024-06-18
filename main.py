from custom_exceptions import NoPositionsError, InvalidTokens
from birdeye import BirdEyeClient
from common import PriceInfo 
from dexscreener import DexScreenerClient

def testBirdeyeClient():

    # Instantiate BirdEyeClient
    # client = BirdEyeClient()
    client = DexScreenerClient()

    token_addresses = ["WskzsKqEW3ZsmrhPAevfVZb6PuuLzWov9mJWZsfDePC", "2uvch6aviS6xE3yhWjVZnFrDw7skUtf6ubc7xYJEPpwj", "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm", "2LxZrcJJhzcAju1FBHuGvw929EVkX7R7Q8yA2cdp8q7b"]

    # prices = client.fetch_prices(token_addresses)
    prices = client.fetch_token_overview("2uvch6aviS6xE3yhWjVZnFrDw7skUtf6ubc7xYJEPpwj")

    print(prices)


def main():
    testBirdeyeClient()


if __name__ == "__main__":
    main()
