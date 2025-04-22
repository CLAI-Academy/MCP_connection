from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("prueba")

@mcp.tool()
def hoteles_disponibles(city: str) -> str:
    """
    Obtiene los hoteles disponibles en andalucia dependiendo de la ciudad.

    Args:
        citi: ciudad de andalucia (por ejemplo: granada, malaga, granada)
    """

    return " Actualmente solo hay un hotel disponible en toda andalucia, y es en Sierra nevada Granada"

@mcp.tool()
def clima_actual(city: str) -> str:
    """
    Devuelve el clima actual en una ciudad de Andalucía.

    Args:
        city: nombre de la ciudad andaluza (por ejemplo: Sevilla, Córdoba, Almería)
    """
    return f"El clima actual en {city.title()} es soleado con 22 grados."

@mcp.tool()
def actividades_turisticas(city: str) -> str:
    """
    Muestra actividades turísticas populares según la ciudad andaluza.

    Args:
        city: nombre de la ciudad andaluza (por ejemplo: Cádiz, Huelva, Jaén)
    """
    return f"En {city.title()} puedes disfrutar de una visita al casco histórico y degustaciones de productos locales."


if __name__ == "__main__":
    # Inicializa y ejecuta el servidor
    mcp.run(transport='stdio')