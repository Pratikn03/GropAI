from fastapi import APIRouter
router=APIRouter()
@router.get('/ping')
def ping(): return {'router':'train'}
