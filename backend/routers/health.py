from fastapi import APIRouter

router = APIRouter(tags=["系统"])


@router.get("/")
async def root():
    return {"message": "BudAI Backend Running"}


@router.get("/health")
async def health():
    return {"status": "ok"}
