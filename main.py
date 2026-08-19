
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from schemas import HealthResponse, PredictionRequest, PredictionResponse

try:
    from predictor import predictor
    MODEL_LOADED = True
except Exception as exc:  # pragma: no cover
    predictor = None
    MODEL_LOADED = False
    _load_error = str(exc)

app = FastAPI(
    title="Insurance Charge Predictor API",
    description="Predicts annual medical insurance charges from a Linear Regression model.",
    version="1.0.0",
)

# Allow the static frontend (served from anywhere, e.g. file:// or a dev server) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse, tags=["meta"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", model_loaded=MODEL_LOADED)


@app.post("/api/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(payload: PredictionRequest) -> PredictionResponse:
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail=f"Model not loaded: {_load_error}")

    try:
        charge, category = predictor.predict(
            age=payload.age,
            sex=payload.sex.value,
            bmi=payload.bmi,
            children=payload.children,
            smoker=payload.smoker.value,
            region=payload.region.value,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc

    return PredictionResponse(
        predicted_charge=charge,
        bmi_category=category,
        inputs=payload,
    )


# Serve the static frontend (index.html, style.css, script.js) at the root.
# Place the built frontend files inside ../frontend and they'll be available
# at http://localhost:8000/
# app.mount("/", StaticFiles(directory="", html=True), name="frontend")
