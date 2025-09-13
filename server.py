"""
EVE Fleet Manager MCP Server - Auto-authorizes fleet on client connection
"""

import time
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from functions import fleet_manager
from static_manage import ShipID_Dict, ShipClass_Dict
from config_load import CONFIG
from IO.API_IO import get_refresh_token
from IO.fleet_api import get_sso_fleetid

# Global state
fleet_mgr: Optional[fleet_manager] = None
fleet_status = {"authorized": False, "error": None, "character": None, "fleet_id": None}

def fleet_authorize_with_retry(max_retries: int = 3, force_refresh: bool = False) -> Dict[str, Any]:
    """Auto-authorize fleet with retry logic"""
    global fleet_mgr, fleet_status
    
    for attempt in range(max_retries):
        try:
            print(f"Fleet authorization attempt {attempt + 1}/{max_retries}")
            
            # Get tokens and initialize
            ship_dict, ship_class_dict = ShipID_Dict(), ShipClass_Dict()
            _, access_token, character_id, character_name = get_refresh_token("refresh_token.txt", force_refresh)
            
            # Create fleet manager
            fleet_id = get_sso_fleetid(access_token, character_id, character_name)
            fleet_mgr = fleet_manager(access_token, fleet_id, character_id, 
                                    bomb_alt_ids=CONFIG.get('ALT_IDS', []), 
                                    ship_dict=ship_dict, ship_class_dict=ship_class_dict)
            
            # Update status
            fleet_status.update({
                "authorized": True, "error": None, 
                "character": character_name, "fleet_id": fleet_id
            })
            
            print(f"[SUCCESS] Fleet authorized for {character_name} (Fleet: {fleet_id})")
            return {"success": True, "character": character_name, "fleet_id": fleet_id, 
                   "fleet_data": fleet_mgr.output_fleet_static()}
            
        except Exception as e:
            error_msg = f"Attempt {attempt + 1} failed: {str(e)}"
            print(error_msg)
            
            if attempt < max_retries - 1:
                time.sleep((attempt + 1) * 2)  # Exponential backoff
            else:
                fleet_status.update({"authorized": False, "error": error_msg})
                return {"success": False, "error": error_msg, "attempts": max_retries}
    
    return {"success": False, "error": "Unexpected error"}

# Create MCP server and auto-authorize
mcp = FastMCP("EVE Fleet Manager")
print("Starting EVE Fleet Manager MCP Server...")
startup_result = fleet_authorize_with_retry()

if startup_result["success"]:
    print(f"[READY] Fleet: {startup_result['fleet_id']}, Character: {startup_result['character']}")
else:
    print(f"[ERROR] Started with authorization error: {startup_result['error']}")

# MCP Tools
@mcp.tool()
def fleet_authorize(force_refresh: bool = False) -> Dict[str, Any]:
    """Manually re-authorize fleet access"""
    return fleet_authorize_with_retry(force_refresh=force_refresh)

@mcp.tool()
def get_fleet_status() -> Dict[str, Any]:
    """Get current fleet status and data"""
    if fleet_mgr and fleet_status["authorized"]:
        try:
            return {**fleet_status, "fleet_data": fleet_mgr.output_fleet_static(), 
                   "members_count": len(fleet_mgr.fleet_members_list)}
        except Exception as e:
            return {**fleet_status, "data_error": str(e)}
    return fleet_status

@mcp.tool()
def refresh_fleet_data() -> Dict[str, Any]:
    """Refresh fleet member data"""
    if not fleet_mgr:
        return {"success": False, "error": "Fleet not authorized"}
    
    try:
        fleet_mgr.renew_members()
        return {"success": True, "fleet_data": fleet_mgr.output_fleet_static(), 
               "members_count": len(fleet_mgr.fleet_members_list)}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Resources
@mcp.resource("fleet://status")
def fleet_status_resource() -> str:
    """Fleet status resource"""
    return f"Fleet Status: {get_fleet_status()}"


# Prompts
@mcp.prompt()
def fleet_prompt(action: str = "status") -> str:
    """Fleet management prompts"""
    prompts = {
        "status": "Show current fleet status and member composition",
        "formation": "Organize fleet into optimal squad formations",
        "invite": "Help invite new members to the fleet",
        "analysis": "Analyze fleet composition and suggest improvements"
    }
    return prompts.get(action, "Help manage EVE Online fleet")
