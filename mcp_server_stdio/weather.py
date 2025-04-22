from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Inicializa el servidor FastMCP
mcp = FastMCP("weather")

# Constantes
NWS_API_BASE = "<https://api.weather.gov>"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Realiza una solicitud a la API de NWS con el manejo de errores adecuado."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    """Formatea una característica de alerta en una cadena legible."""
    props = feature["properties"]
    return f"""
Evento: {props.get('event', 'Unknown')}
Área: {props.get('areaDesc', 'Unknown')}
Severidad: {props.get('severity', 'Unknown')}
Descripción: {props.get('description', 'No description available')}
Instrucciones: {props.get('instruction', 'No specific instructions provided')}
"""

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Obtén alertas meteorológicas para un estado de EE. UU.

    Args:
        state: Código de estado de EE. UU. de dos letras (por ejemplo, CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "No se pueden obtener las alertas o no se encontraron alertas."

    if not data["features"]:
        return "No hay alertas activas para este estado."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\\\\n---\\\\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Obtén el pronóstico del tiempo para una ubicación.

    Args:
        latitude: Latitud de la ubicación
        longitude: Longitud de la ubicación
    """
    # Primero obtén el punto final de la cuadrícula de pronóstico
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "No se pueden obtener los datos del pronóstico para esta ubicación."

    # Obtén la URL del pronóstico de la respuesta de los puntos
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "No se puede obtener el pronóstico detallado."

    # Formatea los períodos en un pronóstico legible
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Solo muestra los próximos 5 períodos
        forecast = f"""
{period['name']}: Temperatura: {period['temperature']}°{period['temperatureUnit']}
Viento: {period['windSpeed']} {period['windDirection']}
Pronóstico: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\\\\n---\\\\n".join(forecasts)

if __name__ == "__main__":
    # Inicializa y ejecuta el servidor
    mcp.run(transport='stdio')