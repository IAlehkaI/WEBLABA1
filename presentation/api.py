from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from domain.models import News
from application.services import NewsService
from infrastructure.repository import PostgresNewsRepository
from infrastructure.db.session import get_db
from presentation.auth import get_api_key
from sqlalchemy.orm import Session

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

def format_date_russian(iso_str: str) -> str:
    months = ["", "января", "февраля", "марта", "апреля", "мая", "июня",
              "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    from datetime import datetime
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return f"{dt.day} {months[dt.month]} {dt.year} г."


templates.env.globals["format_date"] = format_date_russian


# Инициализация сервиса с зависимостью от БД
def get_news_service(db: Session = Depends(get_db)):
    repo = PostgresNewsRepository(db)
    return NewsService(repo)


# === ВЕБ-МАРШРУТЫ (без аутентификации) ===
@router.get("/", response_class=HTMLResponse)
async def home(
        request: Request,
        q: str | None = None,
        service: NewsService = Depends(get_news_service)
):
    search_query = (q or "").strip()
    if search_query:
        all_news = service.search_news(search_query)
        top_news = []
        news_list = all_news
    else:
        all_news = service.get_all_news()
        top_news = all_news[:3]
        news_list = all_news[3:]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "top_news": top_news,
        "news_list": news_list,
        "search_query": search_query
    })


@router.get("/news/{news_id}", response_class=HTMLResponse)
async def news_detail(
        request: Request,
        news_id: int,
        service: NewsService = Depends(get_news_service)
):
    news = service.get_news_by_id(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    return templates.TemplateResponse("news_detail.html", {
        "request": request,
        "news": news
    })


@router.get("/create", response_class=HTMLResponse)
async def create_form(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@router.post("/create")
async def create_news(
    request: Request,
    title: str = Form(...),
    image_url: str = Form(""),
    author: str = Form(...),
    summary: str = Form(...),
    content: str = Form(...),
    tags: str = Form(""),
    service: NewsService = Depends(get_news_service)
):
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    # Передаём created_at как пустую строку — репозиторий сам проставит дату
    news = News(
        id=0,
        title=title,
        author=author,
        content=content,
        summary=summary,
        image_url=image_url,
        tags=tag_list,
        created_at=""  # ← репозиторий проигнорирует это и поставит свою дату
    )
    try:
        service.create_news(news)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        print(f"❌ Ошибка при создании новости: {e}")
        raise HTTPException(status_code=500, detail="Не удалось создать новость")
@router.get("/edit/{news_id}", response_class=HTMLResponse)
async def edit_form(
        request: Request,
        news_id: int,
        service: NewsService = Depends(get_news_service)
):
    news = service.get_news_by_id(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    return templates.TemplateResponse("edit.html", {
        "request": request,
        "news": news,
        "tags_str": ", ".join(news.tags)
    })


@router.post("/edit/{news_id}")
async def update_news(
        request: Request,
        news_id: int,
        title: str = Form(...),
        image_url: str = Form(""),
        author: str = Form(...),
        summary: str = Form(...),
        content: str = Form(...),
        tags: str = Form(""),
        service: NewsService = Depends(get_news_service)
):
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    updated = News(
        id=news_id,
        title=title,
        author=author,
        content=content,
        summary=summary,
        image_url=image_url,
        tags=tag_list,
        created_at=""
    )
    if not service.update_news(news_id, updated):
        raise HTTPException(status_code=404, detail="Новость не найдена")
    return RedirectResponse(url=f"/news/{news_id}", status_code=303)


@router.post("/delete/{news_id}")
async def delete_news(
        request: Request,
        news_id: int,
        service: NewsService = Depends(get_news_service)
):
    if not service.delete_news(news_id):
        raise HTTPException(status_code=404, detail="Новость не найдена")
    return RedirectResponse(url="/", status_code=303)


# === REST API (с аутентификацией) ===
@router.get("/api/news", dependencies=[Depends(get_api_key)])
async def api_get_all(service: NewsService = Depends(get_news_service)):
    return service.get_all_news()


@router.get("/api/news/{news_id}", dependencies=[Depends(get_api_key)])
async def api_get_one(news_id: int, service: NewsService = Depends(get_news_service)):
    news = service.get_news_by_id(news_id)
    if not news:
        raise HTTPException(status_code=404)
    return news


@router.post("/api/news", dependencies=[Depends(get_api_key)])
async def api_create(news: News, service: NewsService = Depends(get_news_service)):
    return service.create_news(news)


@router.put("/api/news/{news_id}", dependencies=[Depends(get_api_key)])
async def api_update(news_id: int, news: News, service: NewsService = Depends(get_news_service)):
    updated = service.update_news(news_id, news)
    if not updated:
        raise HTTPException(status_code=404)
    return updated


@router.delete("/api/news/{news_id}", dependencies=[Depends(get_api_key)])
async def api_delete(news_id: int, service: NewsService = Depends(get_news_service)):
    if not service.delete_news(news_id):
        raise HTTPException(status_code=404)
    return {"status": "deleted"}