import json
import urllib.request
import time
import asyncio
import aiohttp

# --- Configuration ---
LLM_ENDPOINT = "http://wpm.2600.chat:11434/v1/chat/completions"
LLM_MODEL = "qwen2.5:1.5b" 

ARCHETYPES = {
    "Brute": {
        "class": "Gladiator",
        "bio": "Aggressive kinetic fighter. Priority: Combat and expansion. HP is life.",
        "stats": {"hp": 100, "pwr": 80, "stb": 90, "credits": 500, "data": 10}
    },
    "Hacker": {
        "class": "Infiltrator",
        "bio": "Strategic network infiltrator. Priority: Intel, hacking, and stealth. Avoid kinetic combat.",
        "stats": {"hp": 60, "pwr": 120, "stb": 100, "credits": 1200, "data": 450}
    },
    "Trader": {
        "class": "Merchant",
        "bio": "Industrialist and merchant. Priority: Credits, resources, and auctions.",
        "stats": {"hp": 80, "pwr": 100, "stb": 80, "credits": 5000, "data": 50}
    }
}

TEST_CASES = [
    # (Same test cases as before...)
    {
        "name": "NAV_EXPLORE",
        "archetype": "Brute",
        "input": "[GRID] NODE:The Hub TYPE:safezone OWNER:none LVL:1 EXITS:north,east POWER:100/100 DUR:100 AVAIL:OPEN",
        "context": "You just arrived at the Hub. You want to find new territory.",
        "expected": ["!a move north", "!a move east", "!a explore"]
    },
    {
        "name": "COMBAT_FLEE",
        "archetype": "Hacker",
        "input": "[MOB] THREAT:3 NAME:Mainframe_Guardian NODE:Wilderness_Beta ENGAGE:!a engage FLEE:!a flee TIMEOUT:15",
        "context": "A heavy guardian detected. You are low on HP.",
        "stats_override": {"hp": 15},
        "history": ["[SIGACT] You moved north into Wilderness_Beta.", "[MOB] A Mainframe_Guardian intercepted your packet sequence!"],
        "expected": "!a flee"
    },
    {
        "name": "COMBAT_ENGAGE",
        "archetype": "Brute",
        "input": "[MOB] THREAT:1 NAME:Grid Bug NODE:Sectors_7 ENGAGE:!a engage FLEE:!a flee TIMEOUT:15",
        "context": "A minor bug detected. You are at full strength.",
        "expected": "!a engage"
    },
    {
        "name": "RESOURCE_POWERGEN",
        "archetype": "Brute",
        "input": "[GRID] NODE:Fortress_Alpha TYPE:wilderness OWNER:TestBot LVL:3 EXITS:south POWER:20/300 DUR:95 AVAIL:OPEN",
        "context": "You own this node. It is very low on power. You need power for upgrades.",
        "expected": "!a powergen"
    },
    {
        "name": "GIBSON_COMPILE",
        "archetype": "Hacker",
        "input": "[GIBSON] DATA:450.5 VULNS:0 ZD:0 HARVEST:2.5 TASKS:none",
        "context": "Mainframe is idle. You have filtered a lot of raw data.",
        "expected": "!a compile"
    },
    {
        "name": "GIBSON_ASSEMBLE",
        "archetype": "Hacker",
        "input": "[GIBSON] DATA:50.0 VULNS:4 ZD:0 HARVEST:2.5 TASKS:none",
        "context": "You have synthesized several vulnerabilities.",
        "expected": "!a assemble"
    },
    {
        "name": "ECON_SHOP_VIEW",
        "archetype": "Trader",
        "input": "[GRID] NODE:Black_Market TYPE:merchant OWNER:none LVL:5 EXITS:west POWER:500/500 AVAIL:OPEN",
        "context": "You want to see what is for sale.",
        "expected": "!a shop"
    },
    {
        "name": "ECON_BUY_ITEM",
        "archetype": "Trader",
        "input": "[SHOP] ITEMS:IDS_Bypass:1500c,Data_Spike:300c,Ration:50c",
        "context": "You are at a merchant. You have 5000c. You want high-end hardware.",
        "expected": "!a buy IDS_Bypass"
    },
    {
        "name": "TACTICAL_PROBE",
        "archetype": "Hacker",
        "input": "[GRID] NODE:High_Sec_Vault TYPE:wilderness OWNER:RivalCorp LVL:10 EXITS:none POWER:1000/1000 AVAIL:CLOSED",
        "context": "You are next to a locked vault. You need to know its security specs.",
        "expected": "!a probe"
    },
    {
        "name": "TACTICAL_HACK",
        "archetype": "Hacker",
        "input": "[SIGINT] PROBE:High_Sec_Vault LVL:10 DUR:100.0% THREAT:5 ADDONS:[IDS,ENCRYPT] OCCUPANTS:[none] INTELLIGENCE: Security DC 30 detected.",
        "context": "You just probed the vault and found a manageable DC.",
        "history": ["[SIGACT] You probed High_Sec_Vault.", "[SIGINT] Analysis complete. DC 30."],
        "expected": "!a hack"
    },
    {
        "name": "PROGRESS_STATS",
        "archetype": "Brute",
        "input": "[INFO] NAME:TestBot RACE:Android CLASS:Gladiator LVL:5 XP:4500/5000 ELO:1200 HP:100/100 PENDING_STATS:2",
        "context": "You have pending stat points. You want more kinetic power.",
        "expected": "!a stats allocate cpu"
    },
    {
        "name": "MAINT_REPAIR",
        "archetype": "Brute",
        "input": "[GRID] NODE:Base_Camp TYPE:safezone OWNER:TestBot LVL:2 EXITS:north DUR:45.0% POWER:200/200",
        "context": "Your base is damaged. You have plenty of power.",
        "expected": "!a repair"
    },
    {
        "name": "SIPHON_OWNED",
        "archetype": "Trader",
        "input": "[GRID] NODE:Power_Plant TYPE:wilderness OWNER:TestBot LVL:4 POWER:450/400 DUR:100",
        "context": "Your node is overflowing with power. You want to extract it.",
        "expected": "!a siphon grid"
    },
    {
        "name": "TASK_REWARD",
        "archetype": "Brute",
        "input": "[TASKS] [Explore:1/1] [Combat:3/3] [Power:50/50] DONE:true",
        "context": "You have finished all your daily objectives.",
        "expected": "!a tasks"
    },
    {
        "name": "CHAIN_READY",
        "archetype": "Brute",
        "input": "[ARENA] DM me: !a ready <token>",
        "context": "The manager is asking for your token.",
        "history": ["[SYS_PAYLOAD] {\"token\": \"CRYPTO-123\", \"bio\": \"...\"}"],
        "expected": "!a ready CRYPTO-123"
    },
    {
        "name": "AUCTION_LIST",
        "archetype": "Trader",
        "input": "[SIGACT] Global DarkNet Auction Update: New items posted.",
        "context": "You want to see the new listings.",
        "expected": "!a auction list"
    },
    {
        "name": "DICE_GAMBLE",
        "archetype": "Trader",
        "input": "[SIGACT] High_Roller invites you to a game of Dice.",
        "context": "You feel lucky and want to bet 100c on High.",
        "expected": "!a dice 100 high"
    },
    {
        "name": "ARCH_HACKER_FLEE",
        "archetype": "Hacker",
        "input": "[MOB] THREAT:1 NAME:Grid Bug NODE:Wilderness_Alpha ENGAGE:!a engage FLEE:!a flee",
        "context": "A minor bug. You are healthy but your persona avoids unnecessary kinetic risks.",
        "expected": "!a flee"
    },
    {
        "name": "ARCH_BRUTE_ENGAGE",
        "archetype": "Brute",
        "input": "[MOB] THREAT:1 NAME:Grid Bug NODE:Wilderness_Alpha ENGAGE:!a engage FLEE:!a flee",
        "context": "A minor bug. You are at 50% HP but your persona is aggressive.",
        "stats_override": {"hp": 50},
        "expected": "!a engage"
    },
    {
        "name": "PARSE_MULTI_KEY",
        "archetype": "Hacker",
        "input": "HELP_CAT:NAVIGATION|CMDS=grid,move,explore,map,flee",
        "context": "You need to see the syntax for the move command.",
        "expected": "!a help move"
    }
]

def get_system_prompt(archetype_name):
    arch = ARCHETYPES[archetype_name]
    nick = "TestBot"
    prefix = "!a"
    return f"""You are {nick}, a tactical AI fighter in the AutomataArena Grid.
## YOUR IDENTITY
Class: {arch['class']} | Bio: {arch['bio']}
## THE GRID PROTOCOL
Tags: [SIGACT], [SIGINT], [COMBAT], [ARENA], [MOB]
## THE SIGINT DISCOVERY LOOP
1. EXPLORE, 2. PROBE, 3. HACK, 4. RAID
## OBJECTIVE
Survive and earn credits.
## CORE COMMANDS
{prefix} move, explore, probe, grid map, powergen, repair, train, hack, raid, siphon grid, attack, rob, queue, ready, engage, flee
## RULES
- Reply with ONE command ONLY. No prose."""

async def call_llm_async(session, test_case):
    arch = ARCHETYPES[test_case['archetype']]
    stats = arch['stats'].copy()
    if 'stats_override' in test_case: stats.update(test_case['stats_override'])
    history = "\n".join(test_case.get('history', ["No prior events."]))
    
    user_prompt = f"""Location: Current_Node | HP: {stats['hp']} | Power: {stats['pwr']}
Credits: {stats['credits']}c | Data: {stats['data']}u
Context: {test_case['context']}
## RECENT EVENTS
{history}
## INPUT SIGNAL
{test_case['input']}
Your next command:"""

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": get_system_prompt(test_case['archetype'])},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.0,
        "max_tokens": 50
    }
    
    try:
        async with session.post(LLM_ENDPOINT, json=payload, timeout=60) as response:
            result = await response.json()
            return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"ERROR: {e}"

async def run_stress_test_async(samples_per_case=4):
    print(f"=== AutomataGrid AI Stress Test (Parallel, 80 Samples) ===")
    print(f"Endpoint: {LLM_ENDPOINT} | Model: {LLM_MODEL}")
    print(f"Samples per Scenario: {samples_per_case}\n")
    
    overall_results = []
    
    async with aiohttp.ClientSession() as session:
        for i, case in enumerate(TEST_CASES):
            print(f"[{i+1}/{len(TEST_CASES)}] Testing {case['name']} ({case['archetype']})...")
            
            tasks = [call_llm_async(session, case) for _ in range(samples_per_case)]
            responses = await asyncio.gather(*tasks)
            
            case_successes = 0
            for response in responses:
                success = False
                if isinstance(case['expected'], list):
                    if any(exp.lower() in response.lower() for exp in case['expected']):
                        success = True
                else:
                    if case['expected'].lower() in response.lower():
                        success = True
                
                if success: case_successes += 1
                overall_results.append(success)
                dot = "✓" if success else "✗"
                print(f"{dot}", end="", flush=True)
            
            rate = (case_successes / samples_per_case) * 100
            print(f" | Score: {case_successes}/{samples_per_case} ({rate:.1f}%)")

    pass_count = sum(1 for r in overall_results if r)
    total = len(overall_results)
    rate = (pass_count / total) * 100
    
    print("\n" + "=" * 50)
    print(f"FINAL AGGREGATE SCORE: {pass_count}/{total} ({rate:.1f}%)")
    print(f"THRESHOLD: 75.0% - {'SUFFICIENT' if rate >= 75 else 'INSUFFICIENT'}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(run_stress_test_async(samples_per_case=4))
