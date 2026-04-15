# To-Do List

This document tracks active or upcoming, near-term tasks for AutomataArena.

## 🚀 Phase 1: Resource & Grid Foundation (Completed)
- [x] Add `Stability`, `Power`, and `Alignment` columns to `Character` model
- [x] Update `GridNode` model for `is_hidden`, `visibility_mode`, and `irc_affinity`
- [x] Configure `MECHANICS_CFG` in `config.json` for adjustable game balance

## ⚡ Phase 2: Action Economy & Production (Completed)
- [x] Implement `!a powergen` (Active power generation)
- [x] Implement `!a train` (Stability recovery)
- [x] Implement `!a repair` (Node & stability maintenance)
- [x] Implement **Stability Decay** (1% per 24h)
- [x] Integrate Power costs for `move`, `attack`, `hack`
- [x] Integrate Power costs for `explore`

## 📡 Phase 3: Discovery & Cross-Network Messaging (Completed)
- [x] Expand `!a explore` with randomized discovery (Disconnected, NPC, Local, IRC)
- [x] Implement `!a grid network msg <nick> <msg>` for IRC-bridge nodes
- [x] Logic for **Breaching** Closed Networks (Integrity vs Ownership)

## 🏗️ Phase 4: Mainframe Manufacturing (The Gibson) (Completed)
- [x] Implement **The Gibson** background task engine
- [x] Data Compilation logic (100 Data -> 1 Vuln)
- [x] Zero-Day Assembly (4 Vulns -> 1.0 Chain)
- [x] Shared Power Generation Pools for all owned nodes
- [x] Integrate Power costs for compilation (Node Power First)
- [x] Implement **MemoServ** integration for background notifications

## 💰 Phase 5: Global Economy & Mini-Games (Completed)
- [x] Realtime Global **DarkNet Auction** (1% Fee, MemoServ sync)
- [x] **CipherLock** mini-game (NPC access, Data rewards, ICE Lockdown)
- [x] Player-vs-Player **Dice** gambling games
- [x] Global **"High Roller" Leaderboard** (Dice, Arena, etc.)
- [x] Global Economic Ticker (Item/Credit inflation/deflation via LLM)
## 🏴‍☠️ Phase 6: Syndicate Architecture & Polish (Completed)
- [x] **Factions/Teams/Alliances** system (Guild treasuries, private routing)
- [x] **Text map** for IRC (`!a grid map`)
- [x] **Machine-Readable Outputs** (`output mode machine`)
- [x] **AI IQ Upgrade** (v1.6.0 support for all features)
- [x] **Puppet Mode Security** (Owner DMs override AI for 60s)
- [ ] **Graphical map** for web dash
- [ ] **Dynamic Combat Flavor Text** via LLM
- [ ] **Spectator item drops** / interaction
- [ ] **Interactive Spectators** (In-IRC gambling/drops)

## 🏢 Phase 7: Corporate Warfare & Missions (Completed)
- [x] **Syndicate Missions** (Cooperative Power/Sabotage/Slayer goals)
- [x] **72h Declared War** (Formal conflict state + early ceasefire logic)
- [x] **Node Fortification** (Syndicate-wide defense upgrades)
- [x] **Strategic AI Awareness** (Bots respond to Mission/War status)

## ✅ Completed Tasks
- [x] Give Fighter Bots "Short-Term Memory"
- [x] Shop Viewing / Economy Discovery
- [x] Rework Pulse Logic (Pulse on queue/combat only)
- [x] Ambient World Ticker
- [x] Public Echoes/SIGACTs
- [x] Add `x options`, `x news`, `x info` commands
- [x] Node claiming mechanics
- [x] NPC Balance pass
- [x] Spectator rewards for chatting
