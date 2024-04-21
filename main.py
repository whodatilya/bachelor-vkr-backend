from fastapi.responses import JSONResponse
from users.routes import router as guest_router, user_router
from auth.route import router as auth_router
from core.security import JWTAuth
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.requests import Request
from starlette.middleware.authentication import AuthenticationMiddleware
from htmls.process_html import process_html



app = FastAPI()
app.include_router(guest_router)
app.include_router(user_router)
app.include_router(auth_router)

# Add Middleware
app.add_middleware(AuthenticationMiddleware, backend=JWTAuth())

@app.get('/')
def health_check():
    return JSONResponse(content={"status": "Running!"})

@app.post("/uploadByFile", response_class=JSONResponse)
async def upload(request: Request, file: UploadFile = File(...)):
    html_content = await file.read()
    res = await process_html(html_content)

    return res

@app.post("/uploadByRaw", response_class=JSONResponse)
async def upload(request: Request, html_content: str = Form(...)):
    res = await process_html(html_content)

    return res