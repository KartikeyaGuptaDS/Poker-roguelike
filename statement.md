# Problem Statement

Most digital poker implementations are built for one purpose: playing poker
hands against other players or the house, with the scoring, rules, and
session ending the moment the hand is over. There is no persistent
progression, no player-driven customization, and no reason to keep playing
beyond the current hand.

**Ante Up!** exists to explore a different question: what does poker look
like as a single-player, roguelike *system* rather than a single game? The
project builds a complete scoring and progression engine on top of standard
poker hand evaluation — one where a "hand" is just the base unit the player
builds around, not the whole game. The player accumulates a customized deck
and a roster of passive bonuses ("Jokers") across a run, manages an in-game
economy, and works toward score targets that scale unpredictably enough to
require real decision-making about risk, timing, and resource management —
all without any external dependencies, GUI framework, or network component,
so the full system fits in a single readable Python codebase.

## Scope

The project delivers a complete, playable, single-session terminal game:

**In scope**
- Poker hand evaluation for 5-card and smaller hands, including three
  "secret" hands beyond the standard 10 (Five of a Kind, Flush House, Flush
  Five).
- A Chips × Mult scoring engine with permanent, purchasable upgrades
  (Planet cards) and passive multipliers (Jokers).
- An 8-Ante, 3-Blind-per-Ante progression structure, plus an Endless
  continuation mode.
- A full shop economy: purchasing, selling, rerolling, and destroying, with
  four categories of purchasable Booster Packs and Vouchers.
- A random-reward ("Tag") system tied to skipping Blinds, with 16 distinct
  effects.
- Input validation for every player-facing prompt, with automatic
  re-prompting on invalid input.
- An automated test suite covering scoring, shop, and Tag logic.

**Out of scope**
- Persistent save/load between sessions (a run exists only for the process's
  lifetime).
- Multiplayer or networked play.
- A graphical interface — the game is deliberately terminal-only.
- Real-money or account systems of any kind.

## Target Users

- **Players who enjoy roguelike deck-builders** (e.g. fans of *Balatro*,
  *Slay the Spire*) who want a lightweight, dependency-free version they can
  run anywhere Python runs.
- **Students and reviewers evaluating the codebase itself**, since the
  project doubles as a worked example of turning a single rules engine
  (poker hand evaluation) into a layered system (scoring → economy →
  random rewards → progression) with a corresponding test suite.

## High-Level Features

- Poker hand evaluation engine (12 hand types)
- Chips × Mult scoring with permanent Planet-card upgrades
- Ante/Blind progression (8 Antes × 3 Blinds) with an Endless mode
- Shop: Jokers, Planet cards, Booster Packs, Vouchers, sell/destroy/reroll
- 16-Tag reward system triggered by skipping Blinds
- A lightweight Boss-encounter variant system
- Re-prompting input validation across every player interaction
- 120-test automated `unittest` suite
