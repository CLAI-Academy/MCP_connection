

# 🧠 Model Context Protocol (MCP) – Clientes y Servidores

<div align="center">
  <img src="./thumbnail/profile.jpg" alt="Profile" width="150" style="border-radius: 50%;">
</div>

Enlace a mi comunidad de Discord:
https://discord.gg/d49rGXxn

Este repositorio contiene ejemplos prácticos y mínimos para entender cómo funciona el **Model Context Protocol (MCP)**, un estándar abierto para conectar modelos de lenguaje (LLMs) con datos y herramientas externas de forma modular y escalable.

---

## 📂 Estructura del repositorio

### 🟦 `mcp_client_stdio/cliente-openai.py` y `mcp_client_stdio/cliente-anthropic.py`

Implementaciones de clientes MCP que se comunican con modelos de lenguaje a través del protocolo MCP:

- `cliente-openai`: Cliente que se conecta a servidores MCP usando la API de OpenAI.
- `cliente-anthropic`: Cliente que utiliza Claude de Anthropic como host para el MCP.

Cada cliente mantiene una conexión 1:1 con un servidor MCP, gestionando la comunicación con los recursos y herramientas.

### 🟨 `/servidor-api` y `/servidor-local`

Ejemplos de servidores MCP que exponen funcionalidades al modelo:

- `servidor-api`: Simula conexión a un servicio externo vía API (ej. información del clima).
- `servidor-local`: Expone archivos o datos locales como recursos accesibles desde el modelo.

Cada servidor MCP puede ofrecer:

- 🔧 **Tools**: Funciones ejecutables por el LLM (function calling).
- 📄 **Resources**: Datos de solo lectura, como si fueran endpoints GET.
- 💬 **Prompts**: Plantillas predefinidas para guiar al modelo.

---

## 🚀 Cómo probarlo

## 🚀 Cómo probarlo

### Paso 1: Configurar el Proyecto del Cliente
```bash
uv init mcp-client
cd mcp-client
uv venv
source .venv/bin/activate  # En Windows: .venv\\Scripts\\activate
uv add mcp anthropic python-dotenv

```

### Paso 2: Configura Tu Clave API
Crea un archivo .env con tu clave API de Anthropic:
```bash
ANTHROPIC_API_KEY=<tu clave aquí>
```
### Paso 3: Implementar el Cliente
El archivo cliente_anthropic.py contendrá la lógica del cliente MCP (ver ejemplo completo en el repositorio).

Incluye:

Inicialización de la sesión y conexión con el servidor MCP

Envío de mensajes a Claude

Llamadas a herramientas dinámicas según la respuesta del modelo

### Paso 4: Ejecuta el Cliente
```bash
uv run cliente_anthropic.py /ruta/al/servidor/weather.py
```
---