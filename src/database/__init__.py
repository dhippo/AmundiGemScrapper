"""Database package"""
from .manager import insert_article, get_articles_count, get_articles_by_source

__all__ = ['insert_article', 'get_articles_count', 'get_articles_by_source']