import urllib.parse
from typing import Optional

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse

import config

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/login")
def spotify_login():
    target = (
        "https://accounts.spotify.com/authorize"
        + "?response_type=code"
        + "&client_id="
        + config.SPOTIFY_CLIENT_ID
        + "&scope="
        + urllib.parse.quote(config.SPOTIFY_SCOPE, safe="~()*!.'")
        + "&redirect_uri="
        + urllib.parse.quote(config.SPOTIFY_REDIRECT_URI, safe="~()*!.'")
    )

    return RedirectResponse(target)


@app.get("/callback")
def spotify_callback(
    code: Optional[str] = None, error: Optional[str] = None, state: Optional[str] = None
):
    if error:
        return PlainTextResponse("Something went wrong")

    if not code:
        return PlainTextResponse("im a teapot", status_code=418)

    form_data = {
        "client_id": config.SPOTIFY_CLIENT_ID,
        "client_secret": config.SPOTIFY_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.SPOTIFY_REDIRECT_URI,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    r = httpx.post(
        "https://accounts.spotify.com/api/token",
        data=form_data,
        headers=headers,
    )
    r.raise_for_status()
    data = r.json()

    return JSONResponse(data)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
