import logging
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from app.providers import Provider, ProviderError, get_provider
from app.schemas import AnalysisRequest, AnalysisResponse

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger("document_analyzer")
app = FastAPI(title="AI Document Analyzer")

@app.exception_handler(ProviderError)
async def provider_error(request: Request, error: ProviderError):
    logger.warning("Analysis provider failure: %s", str(error))
    return JSONResponse(status_code=502, content={"detail": str(error)})

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalysisResponse)
def analyze(data: AnalysisRequest, provider: Provider = Depends(get_provider)):
    result = provider.analyze(data.text)
    logger.info("Analysis completed provider=%s category=%s characters=%d", provider.name, result.category, len(data.text))
    return AnalysisResponse(provider=provider.name, analysis=result)

