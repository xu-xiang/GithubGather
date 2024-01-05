import uvicorn
from fastapi import FastAPI, Request
from githubgather.proxy.proxy_handlers import proxy_to_github
from githubgather.client.github_client import AsyncGitHubClient

app = FastAPI()
client = AsyncGitHubClient()


@app.api_route("/{rest_of_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, rest_of_path: str):
    return await proxy_to_github(request, rest_of_path, client)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
