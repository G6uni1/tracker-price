import pandas as pd
from prophet import Prophet
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def predict_future(history: List[Dict], periods: int = 30) -> Dict:
    if not history:
        return {"error": "Sem dados históricos"}

    df = pd.DataFrame(history)
    df = df[df['price'].notna()]
    if len(df) < 10:
        return {"error": "Histórico insuficiente (mínimo 10 registros)"}

    df_prophet = pd.DataFrame({
        'ds': pd.to_datetime(df['collected_at']),
        'y': df['price'].astype(float)
    })

    try:
        model = Prophet(
            changepoint_prior_scale=0.05,
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False
        )
        model.fit(df_prophet)

        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        forecast_future = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)

        result = {
            "predictions": forecast_future.to_dict(orient='records'),
            "trend": "alta" if forecast_future['yhat'].iloc[-1] > forecast_future['yhat'].iloc[0] else "baixa",
            "last_price": float(df['price'].iloc[-1]),
            "predicted_price": float(forecast_future['yhat'].iloc[-1])
        }
        return result
    except Exception as e:
        logger.error(f"Erro no treinamento: {e}")
        return {"error": "Falha ao gerar previsão"}