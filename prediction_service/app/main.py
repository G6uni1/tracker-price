from fastapi import FastAPI, HTTPException
from .utils import fetch_price_history
from .model import predict_future

app = FastAPI(title="Previsão de Preços - IA")

@app.get("/predict/{product_id}")
async def predict_price(product_id: str):
    try:
        history = await fetch_price_history(product_id, days=90)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar histórico: {e}")

    result = predict_future(history)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/health")
async def health():
    return {"status": "ok"}