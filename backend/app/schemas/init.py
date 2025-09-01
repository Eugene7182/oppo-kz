# Делает папку 'schemas' пакетом и реэкспортирует нужные модели
from .stock_request import StockRequestCreate, StockRequestOut

__all__ = ["StockRequestCreate", "StockRequestOut"]
