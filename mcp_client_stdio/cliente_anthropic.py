import asyncio
import sys
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # carga las variables de entorno desde .env

class MCPClient:
    def __init__(self):
        # Inicializa los objetos de sesión y cliente
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    async def connect_to_server(self, server_script_path: str):
        """Conéctate a un servidor MCP

        Args:
            server_script_path: Ruta al script del servidor (py o js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')

        if not (is_python or is_js):
            raise ValueError("El script del servidor debe ser un archivo .py o .js")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(command=command, args=[server_script_path], env=None)

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

        # Lista las herramientas disponibles
        response = await self.session.list_tools()
        tools = response.tools
        print("\\\\nConectado al servidor con herramientas:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Procesa una consulta utilizando Claude y las herramientas disponibles"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # Llamada inicial a la API de Claude
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # Procesa la respuesta y gestiona las llamadas a herramientas
        final_text = []
        assistant_message_content = []

        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input
                
                # Ejecuta la llamada a la herramienta
                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Llamando a la herramienta {tool_name} con los argumentos {tool_args}]")
                assistant_message_content.append(content)

                messages.append({
                    "role": "assistant",
                    "content": assistant_message_content
                })

                # Extrae directamente el texto del resultado
                if hasattr(result, 'content') and len(result.content) > 0 and hasattr(result.content[0], 'text'):
                    tool_result_content = result.content[0].text
                else:
                    # Fallback en caso de estructura diferente
                    tool_result_content = str(result)
                
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": tool_result_content
                        }
                    ]
                })

                # Obtén la siguiente respuesta de Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                    tools=available_tools
                )

                final_text.append(response.content[0].text)

        return "\\\\n".join(final_text)

    async def chat_loop(self):
        """Ejecuta un bucle de chat interactivo"""
        print("\\\\n¡Cliente MCP Iniciado!")
        print("Escribe tus consultas o 'quit' para salir.")

        while True:
            try:
                query = input("\\\\nConsulta: ").strip()
                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\\\\n" + response)
            except Exception as e:
                print(f"\\\\nError: {str(e)}")

    async def cleanup(self):
        """Limpia los recursos"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Uso: python client.py <ruta_al_script_del_servidor>")
        sys.exit(1)

    client = MCPClient()

    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
