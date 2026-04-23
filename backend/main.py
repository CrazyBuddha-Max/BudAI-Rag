from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import engine, Base
from core.exceptions import register_exception_handlers
from routers import (
    files,
    health,
    auth,
    knowledge_bases,
    users,
    llm_models,
    assistants,
    conversations,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库初始化完成")
    yield
    await engine.dispose()


app = FastAPI(title="BudAI-rag Backend", lifespan=lifespan)

register_exception_handlers(app)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(llm_models.router)
app.include_router(assistants.router)
app.include_router(conversations.router)
app.include_router(knowledge_bases.router)
app.include_router(files.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
