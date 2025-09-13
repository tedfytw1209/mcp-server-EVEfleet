"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

from mcp.server.fastmcp import FastMCP
from functions import fleet_manager
from static_manage import ShipID_Dict, ShipClass_Dict
from config_load import CONFIG
from IO.API_IO import get_refresh_token
from IO.fleet_api import get_sso_fleetid

#fleet get function

def fleet_reset(access_token, character_id, character_name, ship_dict, ship_class_dict, CONFIG):
    print("[INFO] Fleet reset triggered")
    try:
        fleet_id = get_sso_fleetid(access_token, character_id, character_name)
        fleet = fleet_manager(access_token, fleet_id, character_id, bomb_alt_ids=CONFIG.get('ALT_IDS', []), ship_dict=ship_dict, ship_class_dict=ship_class_dict)
        return fleet.output_fleet_static()
    except Exception as e:
        print(f"[ERROR] Failed to reset fleet: {e}")
        return {'error': 'Failed to reset fleet'}

# Create an MCP server
mcp = FastMCP("EVE Fleet Manager")
#refresh_token, access_token, character_id, character_name = get_refresh_token(file_name="refresh_token.txt")
#fleet = fleet_reset(access_token, character_id, character_name, ship_dict, ship_class_dict, CONFIG=CONFIG)

# Add an addition tool
@mcp.tool()
def fleet_authorize() -> dict:
    """Authorize the fleet"""
    ship_dict = ShipID_Dict()
    ship_class_dict = ShipClass_Dict()
    refresh_token, access_token, character_id, character_name = get_refresh_token(file_name="refresh_token.txt")
    fleet_result = fleet_reset(access_token, character_id, character_name, ship_dict, ship_class_dict, CONFIG=CONFIG)
    return fleet_result

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# Add a prompt
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."