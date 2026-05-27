from fastapi import FastAPI

from .config import settings
from .routers import authorize, internal, metadata, oauth, signup


app = FastAPI(title="Envel Auth")
app.include_router(metadata.router)
app.include_router(authorize.router)
app.include_router(oauth.router)
app.include_router(signup.router)
app.include_router(internal.router)

print(f"Auth server: AUTH_BASE_URL={settings.auth_base_url}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
