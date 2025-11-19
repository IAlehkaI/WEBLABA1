from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models import News
from infrastructure.db.session import SessionLocal
from infrastructure.db.models import NewsDB
from sqlalchemy.orm import Session


class AbstractNewsRepository(ABC):
    @abstractmethod
    def create(self, news: News) -> News:
        pass

    @abstractmethod
    def get_all(self) -> List[News]:
        pass

    @abstractmethod
    def get_by_id(self, news_id: int) -> Optional[News]:
        pass

    @abstractmethod
    def update(self, news_id: int, news: News) -> Optional[News]:
        pass

    @abstractmethod
    def delete(self, news_id: int) -> bool:
        pass

    @abstractmethod
    def search(self, query: str) -> List[News]:
        pass


class PostgresNewsRepository(AbstractNewsRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, db_news: NewsDB) -> News:
        return News(
            id=db_news.id,
            title=db_news.title,
            author=db_news.author,
            content=db_news.content,
            summary=db_news.summary,
            image_url=db_news.image_url or "",
            tags=db_news.tags or [],
            created_at=db_news.created_at.isoformat()
        )

    def create(self, news: News) -> News:
        db_news = NewsDB(
            title=news.title,
            author=news.author,
            content=news.content,
            summary=news.summary,
            image_url=news.image_url,
            tags=news.tags,
            created_at=datetime.utcnow()
        )
        self.db.add(db_news)
        self.db.commit()
        self.db.refresh(db_news)
        return self._to_domain(db_news)

    def get_all(self) -> List[News]:
        db_news = self.db.query(NewsDB).order_by(NewsDB.created_at.desc()).all()
        return [self._to_domain(n) for n in db_news]

    def get_by_id(self, news_id: int) -> Optional[News]:
        db_news = self.db.query(NewsDB).filter(NewsDB.id == news_id).first()
        return self._to_domain(db_news) if db_news else None

    def update(self, news_id: int, news: News) -> Optional[News]:
        db_news = self.db.query(NewsDB).filter(NewsDB.id == news_id).first()
        if not db_news:
            return None

        db_news.title = news.title
        db_news.author = news.author
        db_news.content = news.content
        db_news.summary = news.summary
        db_news.image_url = news.image_url
        db_news.tags = news.tags

        self.db.commit()
        self.db.refresh(db_news)
        return self._to_domain(db_news)

    def delete(self, news_id: int) -> bool:
        db_news = self.db.query(NewsDB).filter(NewsDB.id == news_id).first()
        if not db_news:
            return False
        self.db.delete(db_news)
        self.db.commit()
        return True

    def search(self, query: str) -> List[News]:
        query = f"%{query.lower()}%"
        db_news = self.db.query(NewsDB).filter(
            (NewsDB.title.ilike(query)) |
            (NewsDB.author.ilike(query)) |
            (NewsDB.summary.ilike(query)) |
            (NewsDB.content.ilike(query))
        ).order_by(NewsDB.created_at.desc()).all()
        return [self._to_domain(n) for n in db_news]