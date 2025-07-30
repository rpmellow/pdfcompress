from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pypdf import PdfReader, PdfWriter
from PyPDF2 import PdfReader as PR, PdfWriter as PW
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(directory="templates")

# Serve HTML form at "/"
@app.get("/", response_class=HTMLResponse)
async def serve_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.post("/compress")
async def compress_pdf(file: UploadFile = File(...)):
    # Step 1: First compression using pypdf
    input_bytes = await file.read()
    buffer_in = BytesIO(input_bytes)
    reader = PdfReader(buffer_in)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    if reader.metadata is not None:
        writer.add_metadata(reader.metadata)
    # Compress images if any (optional)
    for page in writer.pages:
        for img in page.images:
            if img.image.mode != "RGBA":
                img.replace(img.image, quality=20)
    # Write to intermediate in-memory buffer
    intermediate = BytesIO()
    writer.write(intermediate)
    intermediate.seek(0)
    # Step 2: Further compress using PyPDF2
    reader2 = PR(intermediate)
    writer2 = PW()
    for page in reader2.pages:
        page.compress_content_streams()
        writer2.add_page(page)
    # Final output to buffer
    final_output = BytesIO()
    writer2.write(final_output)
    final_output.seek(0)
    return StreamingResponse(
        final_output,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"}
    )



class InputText(BaseModel):
    text: str

@app.post("/api/chat")
async def chat_api(input: InputText):
    # Replace this with your actual logic
    return {"response": f"You said: {input.text}"}
