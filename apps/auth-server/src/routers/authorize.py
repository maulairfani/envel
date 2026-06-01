from fastapi import APIRouter, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse

from .. import services

router = APIRouter()


@router.get("/authorize", response_class=HTMLResponse)
def authorize(
    client_id: str = Query(""),
    redirect_uri: str = Query(""),
    state: str = Query(""),
    code_challenge: str = Query(""),
) -> HTMLResponse:
    return HTMLResponse(f"""
      <form method="post" action="/login"
            style="font-family:sans-serif;max-width:300px;margin:5em auto">
        <h3>Login</h3>
        <input name="username" placeholder="username" autofocus
               style="display:block;width:100%;margin-bottom:.5em">
        <input name="password" type="password" placeholder="password"
               style="display:block;width:100%;margin-bottom:.5em">
        <input type="hidden" name="client_id"      value="{client_id}">
        <input type="hidden" name="redirect_uri"   value="{redirect_uri}">
        <input type="hidden" name="state"          value="{state}">
        <input type="hidden" name="code_challenge" value="{code_challenge}">
        <button style="width:100%">Login</button>
      </form>
    """)


@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    redirect_uri: str = Form(...),
    state: str = Form(""),
    client_id: str = Form(""),
    code_challenge: str = Form(""),
):
    code = services.issue_code(username, password, redirect_uri)
    if code is None:
        return HTMLResponse("Login failed", status_code=401)
    return RedirectResponse(
        f"{redirect_uri}?code={code}&state={state}",
        status_code=302,
    )
