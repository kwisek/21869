from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from app.cogs.models import Sequence
from app.cogs.pipeline import run_pipeline
from app.cogs.export import export_to_image, export_to_pdf

router = APIRouter()

@router.post("/convert", response_model=Sequence)
async def convert_to_notes(blob: UploadFile = File(...)):
  melody = run_pipeline(bytes=await blob.read())
  return melody

@router.post("/export/img")
async def export_img(sequence: Sequence, notation: str = "STANDARD"):
  bytes = export_to_image(sequence, notation)
  return StreamingResponse(bytes, media_type="image/jpeg")
    
@router.post("/export/pdf")
async def export_pdf(sequence: Sequence, notation: str = "STANDARD"):
  bytes = export_to_pdf(sequence, notation)
  return StreamingResponse(bytes, media_type="file/pdf")