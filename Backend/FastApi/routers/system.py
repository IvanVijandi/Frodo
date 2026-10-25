from fastapi import APIRouter

router = APIRouter(tags=["Sistema"])

@router.get(
    "/",
    summary="Health check del servicio",
    description="Verifica que la API esté activa y respondiendo correctamente."
)
async def ok():
    return {"message": "ok", "service": "MARIA Backend", "version": "2.0.0"}

