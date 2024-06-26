"""
Client for DexScreener APIs
"""

from decimal import Decimal
from typing import Any
import requests

from common import PriceInfo, TokenOverview
from custom_exceptions import InvalidSolanaAddress, InvalidTokens, NoPositionsError
from utils.helpers import is_solana_address
from vars.constants import SOL_MINT, BASE_DEX_URL

class DexScreenerClient:
    """
    Handler class to assist with all calls to DexScreener API
    """

    @property
    def _headers(self):
        return {
            "accept": "application/json",
        }

    @staticmethod
    def _validate_token_address(token_address: str):
        """
        Validates token address to be a valid solana address

        Args:
            token_address (str): Token address to validate

        Returns:
            None: If token address is valid

        Raises:
            NoPositionsError: If token address is empty
            InvalidSolanaAddress: If token address is not a valid solana address
        """
        if not token_address:
            raise NoPositionsError()

        if not is_solana_address(token_address):
            raise InvalidSolanaAddress()
        
        return None



    def _validate_token_addresses(self, token_addresses: list[str]):
        """
        Validates token addresses to be a valid solana address

        Args:
            token_addresses (list[str]): Token addresses to validate

        Returns:
            None: If token addresses are valid

        Raises:
            NoPositionsError: If token addresses are empty
            InvalidSolanaAddress: If any token address is not a valid solana address
        """
        if not token_addresses:
            raise NoPositionsError()

        for token_address in token_addresses:
            if not token_address:
                raise NoPositionsError()

            if not is_solana_address(token_address):
                raise InvalidSolanaAddress()

        return None


    @staticmethod
    def _validate_response(resp: requests.Response):
        """
        Validates response from API to be 200

        Args:
            resp (requests.Response): Response from API

        Returns:
            None: If response is 200

        Raises:
            InvalidTokens: If response is not 200
        """
        if resp.status_code != 200:
            raise InvalidTokens()

    def _call_api(self, token_address: str) -> dict[str, Any]:
        """
        Calls DexScreener API for a single token

        Args:
            token_address (str): Token address for which to fetch data

        Returns:
            dict[str, Any]: JSON response from API

        Raises:
            InvalidTokens: If response is not 200
            NoPositionsError: If token address is empty
            InvalidSolanaAddress: If token address is not a valid solana address
        """
        self._validate_token_address(token_address)

        url = BASE_DEX_URL + token_address
        response = requests.get(url, headers=self._headers)
        self._validate_response(response)
        data = response.json()
        return data


    def _call_api_bulk(self, token_addresses: list[str]) -> dict[str, Any]:
        """
        Calls DexScreener API for multiple tokens

        Args:
            token_addresses (list[str]): Token addresses for which to fetch data

        Returns:
            dict[str, Any]: JSON response from API

        Raises:
            InvalidTokens: If response is not 200
            NoPositionsError: If token addresses are empty
            InvalidSolanaAddress: If any token address is not a valid solana address
        """
        self._validate_token_addresses(token_addresses)

        url = BASE_DEX_URL + ",".join(token_addresses)
        response = requests.get(url, headers=self._headers)
        self._validate_response(response)
        data = response.json()
        return data

    def fetch_prices_dex(self, token_addresses: list[str]) -> dict[str, PriceInfo[Decimal, Decimal]]:
        """
        For a list of tokens fetches their prices
        via multi API ensuring each token has a price

        Args:
            token_addresses (list[str]): A list of tokens for which to fetch prices

        Returns:
           dict[str, dict[Decimal, PriceInfo[str, Decimal]]: Mapping of token to a named tuple PriceInfo with price and liquidity in Decimal

        """
        self._validate_token_addresses(token_addresses)
        prices = {}

        for token_address in token_addresses:
            data = self._call_api(token_address)
            price_usd = Decimal(data["pairs"][0]["priceUsd"]) if "priceUsd" in data["pairs"][0] else Decimal(0.0)
            liquidity_usd = Decimal(data["pairs"][0]["liquidity"]["usd"]) if "liquidity" in data["pairs"][0] and "usd" in data["pairs"][0]["liquidity"] else Decimal(0.0)

            price_info = PriceInfo(value=price_usd, liquidity=liquidity_usd)
            prices[token_address] = price_info
        return prices



    def fetch_token_overview(self, address: str) -> TokenOverview:
        """
        For a token fetches their overview
        via Dex API ensuring each token has a price

        Args:
        address (str): A token address for which to fetch overview

        Returns:
        TokenOverview: Overview with a lot of token information I don't understand
        """
        self._validate_token_address(address)

        data = self._call_api(address)

        if "pairs" in data and data["pairs"]:
            pair = data["pairs"][0]
            base_token = pair["baseToken"]
            price_usd = Decimal(pair.get("priceUsd", 0))
            liquidity_usd = Decimal(pair["liquidity"].get("usd", 0))
            supply = pair.get("supply", "")

            token_overview = TokenOverview(
                price=price_usd,
                symbol=base_token["symbol"],
                decimals=base_token.get("decimals", ""),
                lastTradeUnixTime=pair.get("pairCreatedAt", None),
                liquidity=liquidity_usd,
                supply=supply
            )

            return token_overview


    @staticmethod
    def find_largest_pool_with_sol(token_pairs, address):
        max_entry = {}
        max_liquidity_usd = -1

        for entry in token_pairs:
            if entry.get("baseToken", {}).get("address") == address and entry["quoteToken"]["address"] == SOL_MINT:
                liquidity_usd = float(entry.get("liquidity", {}).get("usd", 0))
                if liquidity_usd > max_liquidity_usd:
                    max_liquidity_usd = liquidity_usd
                    max_entry = entry
        return max_entry
