import Config
import requests
from common import PriceInfo, TokenOverview
from decimal import Decimal
from custom_exceptions import NoPositionsError, InvalidTokens, InvalidSolanaAddress
from vars.constants import BASE_PRICES_MULTI_URL, BASE_TOKEN_OVERVIEW_URL
class BirdEyeClient:
    """
    Handler class to assist with all calls to BirdEye API
    """

    @property
    def _headers(self):
        return {
            "accept": "application/json",
            "x-chain": "solana",
            "X-API-KEY": Config.BIRD_EYE_TOKEN,
        }

    def _make_api_call(self, method: str, query_url: str, *args, **kwargs) -> requests.Response:
        match method.upper():
            case "GET":
                query_method = requests.get
            case "POST":
                query_method = requests.post
            case _:
                raise ValueError(f'Unrecognised method "{method}" passed for query - {query_url}')
        resp = query_method(query_url, *args, headers=self._headers, **kwargs)
        return resp

    def fetch_prices(self, token_addresses: list[str]) -> dict[str, PriceInfo[Decimal, Decimal]]:
        """
        For a list of tokens fetches their prices
        via multi-price API ensuring each token has a price

        Args:
            token_addresses (list[str]): A list of tokens for which to fetch prices

        Returns:
           dict[str, dict[str, PriceInfo[Decimal, Decimal]]: Mapping of token to a named tuple PriceInfo with price and liquidity

        Raises:
            NoPositionsError: Raise if no tokens are provided
            InvalidToken: Raised if the API call was unsuccessful
        """
      
        if not token_addresses:
            # Raise if no tokens are provided
            raise NoPositionsError()

        prices = {}

        try:
            query_url = BASE_PRICES_MULTI_URL + "&list_address=" + ",".join(token_addresses)
            resp = self._make_api_call("GET", query_url)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("success", False):
                raise InvalidTokens()
                

            for token_address, info in data["data"].items():
                if info:
                    value = Decimal(info.get("value", None))
                    liquidity = Decimal(info.get("liquidity", None))
                    price_info = PriceInfo(value=value, liquidity=liquidity)
                    prices[token_address] = price_info
                else:
                    prices[token_address] = None

            return prices

        except requests.RequestException as e:
            # Raised if the API call was unsuccessful
            raise InvalidTokens()

        


    def fetch_token_overview(self, address: str) -> TokenOverview:
        """
        For a token fetches their overview
        via multi-price API ensuring each token has a price

        Args:
            address (str): A token address for which to fetch overview

        Returns:
            dict[str, float | str]: Overview with a lot of token information I don't understand

        Raises:
            InvalidSolanaAddress: Raise if invalid solana address is passed
            InvalidToken: Raised if the API call was unsuccessful
       """
        """
        Here I have implemented the Token - Overview API but It gives Unauthorized by using the provided API Key. 
        But If We use Multi Prices API then this implementation will be similar to the above one!
        """
        if not address:
            raise InvalidSolanaAddress

        try:
            query_url = BASE_TOKEN_OVERVIEW_URL + '?address=' + address
            resp = self._make_api_call("GET", query_url)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("success", False):
                raise InvalidTokens()

            token_data = data.get("data", {})
            if not token_data:
                raise InvalidTokens()

            token_overview = TokenOverview(
                price=token_data.get("value", None),
                symbol=token_data.get("symbol", ""),
                decimals=token_data.get("decimals", ""),
                lastTradeUnixTime=token_data.get("updateUnixTime", None),
                liquidity=token_data.get("liquidity", None),
                supply=token_data.get("supply", "")
            )

            return token_overview

        except requests.RequestException as e:
            # Raise InvalidTokens if API call was unsuccessful
            raise InvalidTokens()
