from typing import List, Optional
from domain.models import News
from infrastructure.repository import AbstractNewsRepository

class NewsService:
    def __init__(self, repo: AbstractNewsRepository):
        self.repo = repo

    def create_news(self, news: News) -> News:
        return self.repo.create(news)

    def get_all_news(self) -> List[News]:
        return self.repo.get_all()

    def get_news_by_id(self, news_id: int) -> Optional[News]:
        return self.repo.get_by_id(news_id)

    def update_news(self, news_id: int, news: News) -> Optional[News]:
        return self.repo.update(news_id, news)

    def delete_news(self, news_id: int) -> bool:
        return self.repo.delete(news_id)

    def search_news(self, query: str) -> List[News]:
        return self.repo.search(query)