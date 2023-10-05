from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def get_health():
    return {
        'status': 'ok',
        'alive': True
    }
