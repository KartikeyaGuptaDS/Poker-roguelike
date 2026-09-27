import random

from scoring import HAND_INFO
from display import show_shop_message
from shop import BOOSTER_SIZES, open_booster_pack

# ---------------------------------------------------------------------------
# TAG POOL - awarded at random whenever a Small or Big Blind is skipped.
# ---------------------------------------------------------------------------
# "kind" drives how award_random_tag() below handles each one:
#   instant_money_double  - doubles current money now (capped at +$40)
#   instant_orbital       - +3 levels to a random Poker Hand now
#   instant_juggle        - +3 hand size for the very next round only
#   instant_reroll_boss   - rerolls this Ante's Boss Blind encounter now
#   instant_pack          - opens a free pack right on the spot
#   queued_boss_money     - pays out $ once the upcoming Boss Blind is cleared
#   queued_joker_rarity   - next shop gets a free Joker of the given rarity
#   queued_common_bonus   - next shop's next Common Joker is free + boosted
#   queued_free_shop      - next shop's initial cards/packs are 100% free
#   queued_cheap_reroll   - next shop's rerolls start at $0
#   queued_extra_voucher  - next shop gets +1 Voucher slot

TAG_POOL = [
    {"id": "uncommon", "name": "Uncommon Tag", "kind": "queued_joker_rarity", "rarity": "Uncommon",
     "desc": "The next shop contains a free Uncommon Joker."},

    {"id": "rare", "name": "Rare Tag", "kind": "queued_joker_rarity", "rarity": "Rare",
     "desc": "The next shop contains a free Rare Joker."},

    {"id": "chip", "name": "Chip Tag", "kind": "queued_common_bonus", "bonus_type": "chips", "bonus_value": 50,
     "desc": "The next Common Joker in the shop is free and gives +50 Chips."},

    {"id": "base_mult", "name": "Base Multiplier Tag", "kind": "queued_common_bonus", "bonus_type": "mult", "bonus_value": 10,
     "desc": "The next Common Joker in the shop is free and gives +10 Mult."},

    {"id": "mult", "name": "Multiplier Tag", "kind": "queued_common_bonus", "bonus_type": "xmult", "bonus_value": 1.5,
     "desc": "The next Common Joker in the shop is free and gives x1.5 Mult."},

    {"id": "meteor", "name": "Meteor Tag", "kind": "instant_pack", "pack_kind": "Celestial", "size": "Mega",
     "desc": "Opens a free Mega Celestial Pack (choose 2 of 5 Planet cards)."},

    {"id": "standard", "name": "Standard Tag", "kind": "instant_pack", "pack_kind": "Standard", "size": "Mega",
     "desc": "Opens a free Mega Standard Pack (choose 2 of 5 playing cards)."},

    {"id": "buffoon", "name": "Buffoon Tag", "kind": "instant_pack", "pack_kind": "Buffoon", "size": "Mega",
     "desc": "Opens a free Mega Buffoon Pack (choose 2 of 5 Jokers)."},

    {"id": "economy", "name": "Economy Tag", "kind": "instant_money_double",
     "desc": "Doubles your current cash (up to a maximum of +$40)."},

    {"id": "investment", "name": "Investment Tag", "kind": "queued_boss_money", "value": 25,
     "desc": "Grants +$25 after you defeat the upcoming Boss Blind."},

    {"id": "coupon", "name": "Coupon Tag", "kind": "queued_free_shop",
     "desc": "Initial items and booster packs in the next shop are 100% free."},

    {"id": "d6", "name": "D6 Tag", "kind": "queued_cheap_reroll",
     "desc": "Rerolls in the next shop start at $0."},

    {"id": "voucher", "name": "Voucher Tag", "kind": "queued_extra_voucher",
     "desc": "Adds 1 additional Voucher to the next shop."},

    {"id": "boss", "name": "Boss Tag", "kind": "instant_reroll_boss",
     "desc": "Instantly rerolls the current Ante's Boss Blind to a different Boss encounter."},

    {"id": "orbital", "name": "Orbital Tag", "kind": "instant_orbital",
     "desc": "Immediately upgrades a random Poker Hand by +3 levels."},

    {"id": "juggle", "name": "Juggle Tag", "kind": "instant_juggle",
     "desc": "Gives +3 Hand Size for the very next round only."},
]

BOSS_EFFECTS = [
    {"id": "boss_mouth", "name": "The Mouth", "target_mult": 1.6, "desc": "A hungry but weak Boss Blind."},
    {"id": "boss_hook", "name": "The Hook", "target_mult": 1.8, "desc": "A lighter-than-usual Boss Blind."},
    {"id": "boss_arm", "name": "The Arm", "target_mult": 2.0, "desc": "A standard Boss Blind."},
    {"id": "boss_eye", "name": "The Eye", "target_mult": 2.2, "desc": "A sharp-eyed, tougher Boss Blind."},
    {"id": "boss_wall", "name": "The Wall", "target_mult": 2.5, "desc": "A brutally tough Boss Blind."},
]


def pick_boss_effect(current=None):

    choices = [b for b in BOSS_EFFECTS if not current or b["id"] != current["id"]]
    return random.choice(choices or BOSS_EFFECTS)


def make_instant_pack(pack_kind, size):
    spec = BOOSTER_SIZES[size]
    return {
        "name": f"{size} {pack_kind} Pack (Free)",
        "kind": pack_kind,
        "size": size,
        "cost": 0,
        "offer_count": spec["offer"],
        "pick_count": spec["pick"],
    }


def award_random_tag(state, max_slots):
    """Called when a Small or Big Blind is skipped. Picks one random Tag,
    applies its effect (immediately if instant, or queues it for the next
    shop visit otherwise). Returns the tag awarded; if it was a Juggle Tag,
    the caller should add the hand-size bonus to the current hand right
    away (see `juggle_gain` on the returned dict)."""

    tag = random.choice(TAG_POOL)
    kind = tag["kind"]
    result = {"tag": tag, "juggle_gain": 0}

    show_shop_message(f"{tag['name']}! {tag['desc']}")

    if kind == "instant_money_double":
        gain = min(state["money"], 40)
        state["money"] += gain
        show_shop_message(f"Your cash was doubled: +${gain}!")

    elif kind == "instant_orbital":
        hand_type = random.choice(list(HAND_INFO.keys()))
        state["hand_levels"][hand_type] = state["hand_levels"].get(hand_type, 1) + 3
        show_shop_message(f"{hand_type} jumped to level {state['hand_levels'][hand_type]}!")

    elif kind == "instant_juggle":
        result["juggle_gain"] = 3

    elif kind == "instant_reroll_boss":
        state["boss_effect"] = pick_boss_effect(state.get("boss_effect"))
        show_shop_message(f"This Ante's Boss Blind is now {state['boss_effect']['name']}.")

    elif kind == "instant_pack":
        pack = make_instant_pack(tag["pack_kind"], tag["size"])
        open_booster_pack(pack, state, max_slots)

    elif kind == "queued_boss_money":
        state["investment_bonus"] = state.get("investment_bonus", 0) + tag["value"]

    elif kind == "queued_joker_rarity":
        state.setdefault("pending_joker_grants", []).append({"rarity": tag["rarity"], "tag_bonus": None})

    elif kind == "queued_common_bonus":
        state.setdefault("pending_joker_grants", []).append(
            {"rarity": "Common", "tag_bonus": {"type": tag["bonus_type"], "value": tag["bonus_value"]}}
        )

    elif kind == "queued_free_shop":
        state["free_shop_tag"] = True

    elif kind == "queued_cheap_reroll":
        state["cheap_reroll_tag"] = True

    elif kind == "queued_extra_voucher":
        state["extra_voucher_tag"] = True

    return result