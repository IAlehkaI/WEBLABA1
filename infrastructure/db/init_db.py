# infrastructure/db/init_db.py

import os
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from infrastructure.db.session import init_db, engine
from infrastructure.db.models import NewsDB
from sqlalchemy.orm import Session
from datetime import datetime
import json


def load_initial_data():
    if os.getenv("SKIP_INIT_DATA", "false").lower() == "true":
        return

    db = Session(engine)
    if db.query(NewsDB).count() == 0:
        data_path = Path("/app/data/initial_news.json")
        if data_path.exists():
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for item in data:
                db_news = NewsDB(
                    id=item["id"],
                    title=item["title"],
                    author=item["author"],
                    content=item["content"],
                    summary=item["summary"],
                    image_url=item.get("image_url", ""),
                    tags=item.get("tags", []),
                    created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
                )
                db.add(db_news)
            db.commit()
            print(f"✓ Загружено {len(data)} новостей")
        else:
            print("Файл initial_news.json не найден")
    else:
        print("ℹБаза уже содержит данные — пропускаем инициализацию")
    db.close()


if __name__ == "__main__":
    init_db()
    load_initial_data()