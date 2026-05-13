class AppException(Exception):
    pass


class CoinGeckoRequestError(AppException):
    pass


class CoinNotFoundError(AppException):
    pass


class NotEnoughMarketDataError(AppException):
    pass