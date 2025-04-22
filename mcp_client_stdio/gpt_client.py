import asyncio
import sys
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = OpenAI()

    async def connect_to_server(self, server_script_path: str):
        """Conéctate a un servidor MCP

        Args:
            server_script_path: Ruta al script del servidor (py o js)
        """

        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")

        if not (is_python or is_js):
            raise ValueError("El script del servidor debe ser un archivo .py o .js")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(command=command, args=[server_script_path], env=None)

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await s