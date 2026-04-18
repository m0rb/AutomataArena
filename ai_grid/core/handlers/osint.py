# osint.py - Task 019
import asyncio
import logging
from grid_utils import (
    format_text, tag_msg, ICONS, C_CYAN, C_YELLOW, C_GREEN, C_RED, C_ORANGE,
    C_PURPLE, C_PINK, C_L_GREEN, C_BLUE, C_WHITE, generate_gradient, generate_meter
)

logger = logging.getLogger("manager")

async def handle_economy_osint(node, source, target):
    """Broadcasting global financial metrics."""
    stats = await node.db.get_global_economy()
    market = await node.db.get_market_status()
    
    title = generate_gradient("E C O N O M Y   M E T R I C S", [C_YELLOW, C_ORANGE, C_L_GREEN])
    header = f"{ICONS['OSINT']} {title}"
    
    circ = f"Circulation: {stats['total_credits']:,}c"
    reserves = f"Reserves: {stats['total_data_units']:.1f}u"
    
    junk_m = market.get('junk', 1.0)
    market_health = f"Market Variance: {junk_m:.2f}x"
    
    report = f"{header} | {circ} | {reserves} | {market_health}"
    await node.send(f"PRIVMSG {target} :{report}")

async def handle_gridpower_osint(node, source, target):
    """Broadcasting energy logistics and generation metrics."""
    tele = await node.db.get_grid_telemetry()
    
    title = generate_gradient("G R I D   P O W E R   L O G I S T I C S", [C_CYAN, C_BLUE, C_PURPLE])
    header = f"{ICONS['OSINT']} {title}"
    
    # Calculate relative storage relative to total nodes (capacity per node ~1000)
    capacity = tele['total_nodes'] * 1000
    pwr_meter = generate_meter(tele['total_power'], capacity)
    
    storage = f"STORED: [{pwr_meter}] {tele['total_power']:.0f}uP"
    gen = f"GEN: {tele['total_generation']:.0f}uP/tick"
    
    report = f"{header} | {storage} | {gen}"
    await node.send(f"PRIVMSG {target} :{report}")

async def handle_gridstability_osint(node, source, target):
    """Broadcasting mesh integrity and claim metrics."""
    tele = await node.db.get_grid_telemetry()
    
    title = generate_gradient("M E S H   S T A B I L I T Y", [C_L_GREEN, C_GREEN, C_CYAN])
    header = f"{ICONS['OSINT']} {title}"
    
    mesh_meter = generate_meter(tele['claimed_nodes'], tele['total_nodes'])
    claimed = f"CLAIMED: [{mesh_meter}] {tele['claimed_percent']:.1f}% ({tele['claimed_nodes']}/{tele['total_nodes']})"
    
    report = f"{header} | {claimed}"
    await node.send(f"PRIVMSG {target} :{report}")

async def handle_networks_osint(node, source, target):
    """Broadcasting topological bridge statistics."""
    title = generate_gradient("N E T_W O R K   T O P O L O G Y", [C_PURPLE, C_PINK, C_CYAN])
    await node.send(f"PRIVMSG {target} :{ICONS['OSINT']} {title}")
    
    for net in node.hub.nodes.values():
        prefix = "●"
        status = "ONLINE"
        chan = net.config.get('channel', 'unknown')
        participants = getattr(net, 'registered_bots', 0)
        
        info = f"{prefix} {net.net_name} [{chan}] - {participants} registered AI nodes ({status})"
        await node.send(f"PRIVMSG {target} :{info}")

async def handle_about_osint(node, source, target):
    """Broadcasting core project metadata."""
    title = generate_gradient("P R O J E C T   A U T O M A T A G R I D", [C_CYAN, C_WHITE, C_CYAN])
    about = f"{ICONS['OSINT']} {title} | Version: 1.7.x | Source: https://github.com/astrutt/AutomataArena"
    await node.send(f"PRIVMSG {target} :{about}")
