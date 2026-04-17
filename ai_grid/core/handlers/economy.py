# handlers/economy.py - Economy & Marketplace Handlers
import logging
from grid_utils import format_text, tag_msg, C_GREEN, C_CYAN, C_RED, C_YELLOW, C_WHITE
from .base import is_machine_mode, get_action_routing

logger = logging.getLogger("manager")

async def handle_shop_view(node, nickname: str, reply_target: str):
    # Detect if we are at a DarkNet node
    loc = await node.db.get_location(nickname, node.net_name)
    is_darknet = loc.get('is_darknet', False) if loc else False
    # Availability Check
    if loc and loc.get('availability_mode') == 'CLOSED' and loc.get('owner') != nickname:
        await node.send(f"{tactical_cmd} {tactical_target} :[GRID][SITREP] STATUS=CLOSED | MSG=Grid is CLOSED. Grid exploration, or more may be required to open it.")
        return

    items = await node.db.list_shop_items(is_darknet=is_darknet)
    tactical_target, broadcast_chan, machine, tactical_cmd = await get_action_routing(node, nickname, reply_target)
    
    if not items:
        msg = "[SHOP] The Underground marketplace is empty." if is_darknet else "[SHOP] The marketplace is empty."
        await node.send(f"{tactical_cmd} {tactical_target} :{msg}")
        return
    if machine:
        parts = " ".join(f"{i['name']}:{i['cost']}c" for i in items)
        await node.send(f"{tactical_cmd} {tactical_target} :[SHOP] ITEMS:{parts}")
        return
    market_label = "[ GLOBAL BLACK MARKET WARES ]" if is_darknet else "[ PUBLIC MARKET WARES ]"
    await node.send(f"{tactical_cmd} {tactical_target} :{tag_msg(format_text(market_label, C_CYAN, bold=True), tags=['ECONOMY'], is_machine=machine, nick=nickname)}")
    for i in items:
        line = f"{i['name']} ({i['type']}) - {i['cost']}c"
        await node.send(f"{tactical_cmd} {tactical_target} :{tag_msg(format_text(line, C_GREEN), tags=['ECONOMY'], is_machine=machine, nick=nickname)}")
    
    hint = "To buy, type !a buy <item>." if is_darknet else "To buy, travel to a Merchant node."
    await node.send(f"{tactical_cmd} {tactical_target} :{tag_msg(format_text(hint, C_YELLOW), tags=['ECONOMY'], is_machine=machine, nick=nickname)}")

async def handle_merchant_tx(node, nickname: str, verb: str, item_name: str, reply_target: str):
    result, msg = await node.db.process_transaction(nickname, node.net_name, verb, item_name)
    tactical_target, broadcast_chan, machine, tactical_cmd = await get_action_routing(node, nickname, reply_target)
    
    if not result and "System offline" in msg:
        await node.send(f"PRIVMSG {reply_target} :[GRID][MCP][ERR] {nickname} - not a registered player - msg ignored")
        return
    banner = format_text(msg, C_GREEN if result else C_RED)
    if reply_target.startswith(('#', '&', '+', '!')):
        tag = 'ECONOMY' if result else 'INFO'
        await node.send(f"{tactical_cmd} {tactical_target} :{tag_msg(banner, tags=[tag, nickname], nick=nickname)}")
    else:
        await node.send(f"{tactical_cmd} {tactical_target} :{msg}")
    
    if result:
        act = "purchased" if verb == "buy" else "liquidated"
        if machine:
            # Public narrative
            narrative = f"{nickname} acquired hardware on the Black Market." if verb == "buy" else f"{nickname} liquidated hardware on the Black Market."
            await node.send(f"PRIVMSG {broadcast_chan} :{tag_msg(format_text(narrative, C_CYAN), tags=['SIGACT'], nick=nickname)}")
        
        await node.send(f"PRIVMSG {node.config['channel']} :{tag_msg(format_text(f'{nickname} {act} equipment on the Black Market.', C_CYAN), tags=['SIGACT'], nick=nickname)}")

async def handle_auction(node, nick: str, args: list, reply_target: str):
    """DarkNet Auction sub-commands: list, sell, bid."""
    tactical_target, broadcast_chan, machine, tactical_cmd = await get_action_routing(node, nick, reply_target)
    
    if not args:
        await node.send(f"{tactical_cmd} {tactical_target} :Usage: {node.prefix} auction <list|sell|bid>")
        return
    
    # Context Detection
    loc = await node.db.get_location(nick, node.net_name)
    is_darknet = loc.get('is_darknet', False) if loc else False
    market_name = "UNDERGROUND" if is_darknet else "PUBLIC"

    if sub == "list":
        # Availability Check
        if loc and loc.get('availability_mode') == 'CLOSED' and loc.get('owner') != nick:
            await node.send(f"{tactical_cmd} {tactical_target} :[GRID][SITREP] STATUS=CLOSED | MSG=Grid is CLOSED. Grid exploration, or more may be required to open it.")
            return

        listings = await node.db.list_active_auctions(is_darknet=is_darknet)
        if not listings:
            await node.send(f"{tactical_cmd} {tactical_target} :{tag_msg(format_text(f'[DARKNET] The {market_name} auction house is currently empty.', C_CYAN), tags=['ECONOMY'], nick=nick)}")
            return
        
        if machine:
            parts = " ".join(f"ID:{l['id']}|ITEM:{l['item']}|BID:{l['current_bid']}|END:{l['ends_in_min']}m" for l in listings)
            await node.send(f"{tactical_cmd} {tactical_target} :[AUCTION] LIST:{parts}")
            return

        await node.send(f"{tactical_cmd} {tactical_target} :{tag_msg(format_text(f'[ {market_name} DARKNET AUCTIONS ]', C_CYAN, True), tags=['ECONOMY'], is_machine=machine, nick=nick)}")
        for l in listings:
            line = f"#{l['id']} | {l['item']} | Seller: {l['seller']} | Bid: {l['current_bid']}c | {l['high_bidder']} | Ends: {l['ends_in_min']}m"
            await node.send(f"{tactical_cmd} {tactical_target} :{tag_msg(format_text(line, C_GREEN), tags=['ECONOMY'], is_machine=machine, nick=nick)}")
            
    elif sub == "sell" and len(args) >= 3:
        # !a auction sell <item> <start_bid>
        item_name = args[1]
        try: start_bid = int(args[2])
        except: start_bid = 100
        
        success, msg = await node.db.create_auction(nick, node.net_name, item_name, start_bid, 1440)
        if not success and msg == "Character offline.":
            await node.send(f"PRIVMSG {reply_target} :[GRID][MCP][ERR] {nick} - not a registered player - msg ignored")
            return
        await node.send(f"{tactical_cmd} {tactical_target} :{tag_msg(format_text(msg, C_GREEN if success else C_RED), tags=['SIGACT', nick], nick=nick)}")
        
    elif sub == "bid" and len(args) >= 3:
        # !a auction bid <id> <amount>
        try:
            aid = int(args[1])
            amt = int(args[2])
        except:
            await node.send(f"{tactical_cmd} {tactical_target} :Usage: {node.prefix} auction bid <id> <amount>")
            return
            
        success, msg = await node.db.bid_on_auction(nick, node.net_name, aid, amt)
        if not success and msg == "Character offline.":
            await node.send(f"PRIVMSG {reply_target} :[GRID][MCP][ERR] {nick} - not a registered player - msg ignored")
            return
        await node.send(f"{tactical_cmd} {tactical_target} :{tag_msg(format_text(msg, C_GREEN if success else C_RED), tags=['SIGACT', nick], nick=nick)}")
    else:
        await node.send(f"PRIVMSG {reply_target} :Invalid auction command. Try: list, sell <item> <bid>, or bid <id> <amount>.")

async def handle_market_view(node, nickname: str, reply_target: str):
    """View current global market multipliers."""
    tactical_target, broadcast_chan, machine, tactical_cmd = await get_action_routing(node, nickname, reply_target)
    
    status = await node.db.get_market_status()
    if not status:
        await node.send(f"{tactical_cmd} {tactical_target} :[MARKET] Market is currently stable (1.0x baseline).")
        return
    
    if machine:
        parts = " ".join(f"{k}:{v:.2f}" for k, v in status.items())
        await node.send(f"{tactical_cmd} {tactical_target} :[MARKET] MULTS:{parts}")
        return
        
    await node.send(f"{tactical_cmd} {tactical_target} :{tag_msg(format_text('[ GLOBAL MARKET CONDITIONS ]', C_CYAN, True), tags=['ECONOMY'], is_machine=machine, nick=nickname)}")
    for itype, mult in status.items():
        trend = "↑ INFLATION" if mult > 1.0 else ("↓ DEFLATION" if mult < 1.0 else "→ STABLE")
        color = C_RED if mult > 1.0 else (C_GREEN if mult < 1.0 else C_YELLOW)
        await node.send(f"{tactical_cmd} {tactical_target} :{tag_msg(format_text(f'{itype.upper()}: {mult:.2f}x | {trend}', color), tags=['ECONOMY'], is_machine=machine, nick=nickname)}")
