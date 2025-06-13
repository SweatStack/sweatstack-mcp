import contextlib

from fastapi import FastAPI

from .server import server


# Create a combined lifespan to manage both session managers
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(server.session_manager.run())
        yield


app = FastAPI(lifespan=lifespan)
app.mount("/mcp/", server.streamable_http_app())