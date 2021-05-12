import os, sys, subprocess

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.templating import Jinja2Templates
from starlette.background import BackgroundTask

import uvicorn
from youtube_dl import YoutubeDL
from collections import ChainMap

templates = Jinja2Templates(directory="")

app_defaults = {
    "YDL_FORMAT": "best[height<=720][ext=mp4]/best[height<=720][ext=mkv]",
    "YDL_EXTRACT_AUDIO_FORMAT": None,
    "YDL_EXTRACT_AUDIO_QUALITY": "192",
    "YDL_RECODE_VIDEO_FORMAT": None,
    "YDL_OUTPUT_TEMPLATE": "/youtube-dl/%(title).200s.%(ext)s",
    "YDL_ARCHIVE_FILE": None,
    "YDL_SERVER_HOST": "0.0.0.0",
    "YDL_SERVER_PORT": 8080,
    "YDL_UPDATE_TIME": "True",
}


async def dl_queue_list(request):
    return templates.TemplateResponse("index.html", {"request": request})


async def q_put(request):
    form = await request.form()
    url = form.get("url").strip()
    options = {"format": form.get("format")}

    if not url:
        return JSONResponse(
            {"success": False, "error": "/q called without a 'url' in form data"}
        )

    task = BackgroundTask(download, url, options)

    print("Added url " + url + " to the download queue")
    return JSONResponse(
        {"success": True, "url": url, "options": options}, background=task
    )


async def update_route(scope, receive, send):
    task = BackgroundTask(update)

    return JSONResponse({"output": "Initiated package update"}, background=task)


def update():
    try:
        output = subprocess.check_output(
            [sys.executable, "-m", "pip", "install", "--upgrade", "youtube-dl"]
        )

        print(output.decode("ascii"))
    except subprocess.CalledProcessError as e:
        print(e.output)

def get_ydl_options(request_options):
    request_vars = {}

    requested_format = request_options.get("format", "720p")

    if requested_format == "1080p":
        request_vars["YDL_FORMAT"] = "best[height=1080][ext=mp4]/best[height=1080][ext=mkv]/bestvideo[height<=1080][ext=mp4]+bestaudio/best[height<=?1080]"
    elif requested_format == "720p":
        request_vars["YDL_FORMAT"] = "best[height=720][ext=mp4]/best[height=720][ext=mkv]/bestvideo[height<=720][ext=mp4]+bestaudio/best[height<=?720]"
    elif requested_format == "best":
        request_vars["YDL_FORMAT"] = "bestvideo[ext=mp4]+bestaudio/best[ext=mp4]/best[ext=mkv]"

    ydl_vars = ChainMap(request_vars, os.environ, app_defaults)

    return {
        "format": ydl_vars["YDL_FORMAT"],
        "outtmpl": ydl_vars["YDL_OUTPUT_TEMPLATE"],
        "download_archive": ydl_vars["YDL_ARCHIVE_FILE"],
        "updatetime": ydl_vars["YDL_UPDATE_TIME"] == "True",
    }


def download(url, request_options):
    with YoutubeDL(get_ydl_options(request_options)) as ydl:
        ydl.download([url])


routes = [
    Route("/youtube-dl", endpoint=dl_queue_list),
    Route("/youtube-dl/q", endpoint=q_put, methods=["POST"]),
    Route("/youtube-dl/update", endpoint=update_route, methods=["PUT"]),
    Mount("/youtube-dl/static", app=StaticFiles(directory="static"), name="static"),
]

app = Starlette(debug=True, routes=routes)

print("Updating youtube-dl to the newest version")
update()

app_vars = ChainMap(os.environ, app_defaults)

if __name__ == "__main__":
    uvicorn.run(
        app, host=app_vars["YDL_SERVER_HOST"], port=int(app_vars["YDL_SERVER_PORT"])
    )
