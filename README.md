[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://raw.githubusercontent.com/manbearwiz/youtube-dl-server/master/LICENSE)

# youtube-dl-server

Web UI and REST interface for downloading youtube videos. [`starlette`](https://github.com/encode/starlette) + [`youtube-dl`](https://github.com/rg3/youtube-dl).

### Format used

- 720p : best[height=1080][ext=mp4]/best[height=1080][ext=mkv]/bestvideo[height<=1080][ext=mp4]+bestaudio/best[height<=?1080]
- 1080p : best[height=720][ext=mp4]/best[height=720][ext=mkv]/bestvideo[height<=720][ext=mp4]+bestaudio/best[height<=?720]
- Best : bestvideo[ext=mp4]+bestaudio/best[ext=mp4]/best[ext=mkv]

## Running

### Docker Compose

This is an example service definition that could be put in `docker-compose.yml`. This service uses a VPN client container for its networking.

```yml
  youtube-dl:
    image: mthevenot/youtube-dl-server
    volumes:
      - /home/youtube-dl:/youtube-dl
    ports:
      - 8080:8080
    restart: unless-stopped
```

## Usage

### Start a download remotely

Downloads can be triggered by supplying the `{{url}}` of the requested video through the Web UI or through the REST interface via curl, etc.

#### HTML

Just navigate to `http://{{host}}:8080/youtube-dl` and enter the requested `{{url}}`.

#### Curl

```shell
curl -X POST --data-urlencode "url={{url}}" http://{{host}}:8080/youtube-dl/q
```

#### Fetch

```javascript
fetch(`http://${host}:8080/youtube-dl/q`, {
  method: "POST",
  body: new URLSearchParams({
    url: url,
    format: "720p"
  }),
});
```

#### Bookmarklet

Add the following bookmarklet to your bookmark bar so you can conviently send the current page url to your youtube-dl-server instance.

```javascript
javascript:!function(){fetch("http://${host}:8080/youtube-dl/q",{body:new URLSearchParams({url:window.location.href,format:"720p"}),method:"POST"})}();
```

## Implementation

The server uses [`starlette`](https://github.com/encode/starlette) for the web framework and [`youtube-dl`](https://github.com/rg3/youtube-dl) to handle the downloading. The integration with youtube-dl makes use of their [python api](https://github.com/rg3/youtube-dl#embedding-youtube-dl).

This docker image is based on [`python:alpine`](https://registry.hub.docker.com/_/python/) and consequently [`alpine:3.8`](https://hub.docker.com/_/alpine/).


## Credits

This repo is a fork from [`manbearwiz/youtube-dl-server`](https://github.com/manbearwiz/youtube-dl-server)