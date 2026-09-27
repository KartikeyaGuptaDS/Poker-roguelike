import random

from card import Card, RANKS, SUITS, RANK_VALUES
from display import (
    show_owned_jokers, show_shop, show_pack_options,
    show_destroy_prompt, show_shop_message,
)
from input_validation import (
    validate_shop_choice, validate_pack_picks, validate_destroy_input, validate_sell_choice,
)

# ---------------------------------------------------------------------------
# JOKER POOL - persistent, run-long effects. Appear both as direct shop
# offers and inside Buffoon Packs.
# ---------------------------------------------------------------------------
JOKER_POOL = [
    {"id": "j_flat_mult", "name": "Joker", "cost": 3, "rarity": "Common",
     "desc": "+4 Mult", "type": "mult", "value": 4},

    {"id": "j_diamond", "name": "Greedy Joker", "cost": 4, "rarity": "Common",
     "desc": "+3 Mult per ♦ in played hand", "type": "mult_suit", "value": 3, "suit": "♦"},

    {"id": "j_heart", "name": "Lusty Joker", "cost": 4, "rarity": "Common",
     "desc": "+3 Mult per ♥ in played hand", "type": "mult_suit", "value": 3, "suit": "♥"},

    {"id": "j_spade", "name": "Wrathful Joker", "cost": 4, "rarity": "Common",
     "desc": "+3 Mult per ♠ in played hand", "type": "mult_suit", "value": 3, "suit": "♠"},

    {"id": "j_club", "name": "Gluttonous Joker", "cost": 4, "rarity": "Common",
     "desc": "+3 Mult per ♣ in played hand", "type": "mult_suit", "value": 3, "suit": "♣"},

    {"id": "j_jolly", "name": "Jolly Joker", "cost": 4, "rarity": "Common",
     "desc": "+8 Mult if played hand contains a Pair", "type": "mult_hand", "value": 8,
     "hands": ["One Pair", "Two Pair", "Three of a Kind", "Full House", "Four of a Kind"]},

    {"id": "j_zany", "name": "Zany Joker", "cost": 4, "rarity": "Common",
     "desc": "+12 Mult if played hand is Three of a Kind or better", "type": "mult_hand", "value": 12,
     "hands": ["Three of a Kind", "Full House", "Four of a Kind", "Five of a Kind", "Flush House"]},

    {"id": "j_mad", "name": "Mad Joker", "cost": 4, "rarity": "Common",
     "desc": "+10 Mult if played hand is Two Pair", "type": "mult_hand", "value": 10,
     "hands": ["Two Pair"]},

    {"id": "j_crazy", "name": "Crazy Joker", "cost": 4, "rarity": "Common",
     "desc": "+12 Mult if played hand is a Straight", "type": "mult_hand", "value": 12,
     "hands": ["Straight", "Straight Flush"]},

    {"id": "j_droll", "name": "Droll Joker", "cost": 4, "rarity": "Common",
     "desc": "+10 Mult if played hand is a Flush", "type": "mult_hand", "value": 10,
     "hands": ["Flush", "Straight Flush", "Flush House", "Flush Five"]},

    {"id": "j_sly", "name": "Sly Joker", "cost": 3, "rarity": "Common",
     "desc": "+50 Chips if played hand contains a Pair", "type": "chips_hand", "value": 50,
     "hands": ["One Pair", "Two Pair", "Three of a Kind", "Full House", "Four of a Kind"]},

    {"id": "j_half", "name": "Half Joker", "cost": 4, "rarity": "Common",
     "desc": "+20 flat Mult", "type": "mult", "value": 20},

    {"id": "j_banner", "name": "Banner", "cost": 4, "rarity": "Common",
     "desc": "+30 Chips per Discard remaining", "type": "chips_per_discard_remaining", "value": 30},

    {"id": "j_blue", "name": "Blue Joker", "cost": 4, "rarity": "Common",
     "desc": "+2 Chips per card remaining in Deck", "type": "chips_per_deck_card", "value": 2},

    {"id": "j_bull", "name": "Bull", "cost": 4, "rarity": "Uncommon",
     "desc": "+2 Chips per $ you have", "type": "chips_per_dollar", "value": 2},

    {"id": "j_scary", "name": "Scary Face", "cost": 3, "rarity": "Common",
     "desc": "+30 Chips per face card (J/Q/K) played", "type": "chips_per_facecard", "value": 30},

    {"id": "j_photo", "name": "Photograph", "cost": 4, "rarity": "Uncommon",
     "desc": "x2 Mult if played hand contains a face card", "type": "xmult_if_facecard", "value": 2},

    {"id": "j_ten", "name": "Ten Fan", "cost": 3, "rarity": "Common",
     "desc": "+20 Chips per 10 played", "type": "chips_per_rank", "value": 20, "rank": "10"},

    {"id": "j_ambitious", "name": "Business Card", "cost": 4, "rarity": "Common",
     "desc": "+$2 every time you play a hand", "type": "money_hand", "value": 2},

    {"id": "j_golden", "name": "Golden Ticket", "cost": 4, "rarity": "Common",
     "desc": "+$3 every time you discard", "type": "money_discard", "value": 3},

    {"id": "j_rocket", "name": "Rocket", "cost": 6, "rarity": "Uncommon",
     "desc": "+5 to your max interest cap", "type": "interest_cap", "value": 5},

    {"id": "j_handsize", "name": "Hand Extender", "cost": 4, "rarity": "Uncommon",
     "desc": "+1 hand size", "type": "hand_size", "value": 1},

    {"id": "j_extrahand", "name": "Trainer's Whistle", "cost": 6, "rarity": "Rare",
     "desc": "+1 hand per round", "type": "extra_hands", "value": 1},

    {"id": "j_extradiscard", "name": "Steady Hands", "cost": 6, "rarity": "Rare",
     "desc": "+1 discard per round", "type": "extra_discards", "value": 1},

    {"id": "j_xmult_rare", "name": "Wild Multiplier", "cost": 8, "rarity": "Rare",
     "desc": "x1.5 Mult", "type": "xmult", "value": 1.5},

    {"id": "j_xmult_legendary", "name": "Cosmic Joker", "cost": 12, "rarity": "Legendary",
     "desc": "x2 Mult", "type": "xmult", "value": 2.0},
]

# ---------------------------------------------------------------------------
# PLANET (Celestial) POOL - instantly level up a hand type's base chips/mult.
# ---------------------------------------------------------------------------
CELESTIAL_POOL = [
    {"id": "pl_pluto", "name": "Pluto", "hand_type": "High Card"},
    {"id": "pl_mercury", "name": "Mercury", "hand_type": "One Pair"},
    {"id": "pl_uranus", "name": "Uranus", "hand_type": "Two Pair"},
    {"id": "pl_venus", "name": "Venus", "hand_type": "Three of a Kind"},
    {"id": "pl_saturn", "name": "Saturn", "hand_type": "Straight"},
    {"id": "pl_jupiter", "name": "Jupiter", "hand_type": "Flush"},
    {"id": "pl_earth", "name": "Earth", "hand_type": "Full House"},
    {"id": "pl_mars", "name": "Mars", "hand_type": "Four of a Kind"},
    {"id": "pl_neptune", "name": "Neptune", "hand_type": "Straight Flush"},
    {"id": "pl_planetx", "name": "Planet X", "hand_type": "Five of a Kind"},
    {"id": "pl_ceres", "name": "Ceres", "hand_type": "Flush House"},
    {"id": "pl_eris", "name": "Eris", "hand_type": "Flush Five"},
]
PLANET_COST = 2

# ---------------------------------------------------------------------------
# VOUCHER POOL - one per run each, only offered right after a Boss Blind.
# ---------------------------------------------------------------------------
VOUCHER_POOL = [
    {"id": "v_hand_size", "name": "Hand Size Voucher", "cost": 8,
     "desc": "Permanently +1 max hand size", "type": "hand_size_perm", "value": 1},
    {"id": "v_extrahand", "name": "Extra Hand Voucher", "cost": 8,
     "desc": "Permanently +1 hand per round", "type": "hands_perm", "value": 1},
    {"id": "v_extradiscard", "name": "Extra Discard Voucher", "cost": 8,
     "desc": "Permanently +1 discard per round", "type": "discards_perm", "value": 1},
    {"id": "v_jokerslot", "name": "Joker Slot Voucher", "cost": 10,
     "desc": "Permanently +1 Joker slot", "type": "joker_slot_perm", "value": 1},
    {"id": "v_interest", "name": "Interest Voucher", "cost": 8,
     "desc": "Permanently +5 to your max interest cap", "type": "interest_cap_perm", "value": 5},
    {"id": "v_reroll", "name": "Reroll Voucher", "cost": 6,
     "desc": "Rerolls cost $2 less (minimum $1)", "type": "reroll_discount", "value": 2},
    {"id": "v_clearance", "name": "Clearance Voucher", "cost": 6,
     "desc": "All shop prices reduced by 20%", "type": "discount", "value": 0.2},
]

# ---------------------------------------------------------------------------
# BOOSTER PACKS - Buffoon (Jokers), Celestial (Planets), Standard (enhanced
# playing cards). Sizes control how many options are shown vs. how many you
# get to keep.
# ---------------------------------------------------------------------------
BOOSTER_SIZES = {
    "Regular": {"offer": 3, "pick": 1, "cost": 3},
    "Jumbo":   {"offer": 5, "pick": 1, "cost": 4},
    "Mega":    {"offer": 5, "pick": 2, "cost": 6},
}
BOOSTER_KINDS = ["Buffoon", "Celestial", "Standard"]
BOOSTER_KIND_COST_MOD = {"Buffoon": 2, "Celestial": 0, "Standard": 0}

JOKER_SLOTS = 5
BASE_REROLL_COST = 4
DESTROY_COST = 3


def get_joker_bonus(jokers, effect_type):

    return sum(j["value"] for j in jokers if j["type"] == effect_type)


def make_enhanced_card():
    rank = random.choice(RANKS)
    suit = random.choice(SUITS)
    value = RANK_VALUES[rank]
    if random.random() < 0.5:
        return Card(rank, suit, value, enhancement="bonus", bonus_chips=30)
    else:
        return Card(rank, suit, value, enhancement="mult", bonus_mult=4)


def make_joker_offer(owned_joker_ids, exclude_ids=()):

    available = [j for j in JOKER_POOL if j["id"] not in owned_joker_ids and j["id"] not in exclude_ids]
    if not available:
        return None
    joker = random.choice(available)
    return {"kind": "joker", "cost": joker["cost"], **joker}


def make_granted_joker_offer(owned_joker_ids, rarity, exclude_ids=()):

    available = [j for j in JOKER_POOL if j["id"] not in owned_joker_ids and j["id"] not in exclude_ids
                 and j["rarity"] == rarity]
    if not available:
        available = [j for j in JOKER_POOL if j["id"] not in owned_joker_ids and j["id"] not in exclude_ids]
    if not available:
        return None
    joker = random.choice(available)
    return {"kind": "joker", "cost": joker["cost"], **joker}


def tag_bonus_desc(tag_bonus):

    t, v = tag_bonus["type"], tag_bonus["value"]
    if t == "chips":
        return f"+{v} Chips"
    elif t == "mult":
        return f"+{v} Mult"
    elif t == "xmult":
        return f"x{v} Mult"
    return ""


def make_planet_offer():

    planet = random.choice(CELESTIAL_POOL)
    return {"kind": "planet", "cost": PLANET_COST, **planet}


CARD_SLOT_COMBOS = ["planet_planet", "joker_joker", "planet_joker"]


def make_card_slots(owned_joker_ids):

    combo = random.choice(CARD_SLOT_COMBOS)

    if combo == "planet_planet":
        return [make_planet_offer(), make_planet_offer()]

    if combo == "joker_joker":
        first = make_joker_offer(owned_joker_ids)
        if first is None:
            # No Jokers left to offer at all - fall back to Planets.
            return [make_planet_offer(), make_planet_offer()]
        second = make_joker_offer(owned_joker_ids, exclude_ids=(first["id"],))
        return [first, second if second is not None else make_planet_offer()]

    # planet_joker
    joker = make_joker_offer(owned_joker_ids)
    slots = [joker, make_planet_offer()] if joker is not None else [make_planet_offer(), make_planet_offer()]
    random.shuffle(slots)
    return slots


def make_booster_offer():

    kind = random.choice(BOOSTER_KINDS)
    size = random.choice(list(BOOSTER_SIZES.keys()))
    spec = BOOSTER_SIZES[size]
    cost = spec["cost"] + BOOSTER_KIND_COST_MOD[kind]
    return {
        "name": f"{size} {kind} Pack",
        "kind": kind,
        "size": size,
        "cost": cost,
        "offer_count": spec["offer"],
        "pick_count": spec["pick"],
    }


class Shop:

    def __init__(self, owned_joker_ids, after_boss, owned_voucher_ids, discount_pct=0.0,
                 pending_joker_grants=None, extra_voucher=False, free_items=False):
        self.owned_joker_ids = list(owned_joker_ids)
        self.discount_pct = discount_pct
        self.reroll_count = 0
        self.free_items = free_items

        self.card_slots = make_card_slots(self.owned_joker_ids)
        self.booster_slots = [make_booster_offer() for _ in range(2)]

        # Guaranteed Tag-granted Joker slots - always free, exempt from
        # reroll, consumed (bought or not) once this shop visit ends.
        self.granted_slots = []
        excluded = set()
        for grant in (pending_joker_grants or []):
            offer = make_granted_joker_offer(self.owned_joker_ids, grant["rarity"], exclude_ids=excluded)
            if offer is None:
                continue
            excluded.add(offer["id"])
            if grant.get("tag_bonus"):
                offer["tag_bonus"] = grant["tag_bonus"]
            self.granted_slots.append(offer)

        # Normally 1 Voucher slot right after a Boss Blind, 0 otherwise;
        # the Voucher Tag adds one more on top of whatever that would be.
        voucher_count = (1 if after_boss else 0) + (1 if extra_voucher else 0)
        available_vouchers = [v for v in VOUCHER_POOL if v["id"] not in owned_voucher_ids]
        self.voucher_slots = []
        for _ in range(voucher_count):
            if not available_vouchers:
                break
            voucher = random.choice(available_vouchers)
            self.voucher_slots.append(voucher)
            available_vouchers = [v for v in available_vouchers if v["id"] != voucher["id"]]

    def price(self, base_cost):

        if base_cost <= 0:
            return 0
        return max(1, round(base_cost * (1 - self.discount_pct)))

    def restock(self):

        self.card_slots = make_card_slots(self.owned_joker_ids)
        self.booster_slots = [make_booster_offer() for _ in range(2)]
        # Granted (Tag) slots and Voucher slots are untouched by reroll.
        # The Coupon Tag's "free" pricing only covers the initial offer.
        self.free_items = False

    def reroll(self):

        self.reroll_count += 1
        self.restock()

    def build_entries(self):

        entries = []
        n = 1

        for i, slot in enumerate(self.granted_slots):
            if slot is None:
                continue
            label = f"[Joker] {slot['name']} (FREE)"
            desc = slot["desc"]
            if slot.get("tag_bonus"):
                desc += f" | Tag bonus: {tag_bonus_desc(slot['tag_bonus'])}"
            entries.append({"number": n, "section": "card", "slot_index": i, "granted": True,
                             "label": label, "cost": 0, "desc": desc, "data": slot})
            n += 1

        for i, slot in enumerate(self.card_slots):
            if slot is None:
                continue
            raw_cost = 0 if self.free_items else slot["cost"]
            if slot["kind"] == "joker":
                label = f"[Joker] {slot['name']}"
                desc = slot["desc"]
            else:
                label = f"[Planet] {slot['name']}"
                desc = f"Upgrades {slot['hand_type']} to the next level"
            entries.append({"number": n, "section": "card", "slot_index": i, "granted": False,
                             "label": label, "cost": self.price(raw_cost),
                             "desc": desc, "data": slot})
            n += 1

        for i, slot in enumerate(self.booster_slots):
            if slot is None:
                continue
            raw_cost = 0 if self.free_items else slot["cost"]
            desc = f"{slot['kind']} Pack - choose {slot['pick_count']} of {slot['offer_count']}"
            entries.append({"number": n, "section": "pack", "slot_index": i, "granted": False,
                             "label": slot["name"], "cost": self.price(raw_cost),
                             "desc": desc, "data": slot})
            n += 1

        for i, voucher in enumerate(self.voucher_slots):
            if voucher is None:
                continue
            entries.append({"number": n, "section": "voucher", "slot_index": i, "granted": False,
                             "label": f"[Voucher] {voucher['name']}",
                             "cost": self.price(voucher["cost"]),
                             "desc": voucher["desc"], "data": voucher})
            n += 1

        return entries


def apply_voucher_effect(voucher, state):
    v_type = voucher["type"]
    value = voucher["value"]

    if v_type == "hand_size_perm":
        state["bonus_hand_size"] += value
    elif v_type == "hands_perm":
        state["bonus_hands"] += value
    elif v_type == "discards_perm":
        state["bonus_discards"] += value
    elif v_type == "interest_cap_perm":
        state["bonus_interest_cap"] += value
    elif v_type == "joker_slot_perm":
        state["bonus_joker_slots"] += value
    elif v_type == "reroll_discount":
        state["reroll_discount"] += value
    elif v_type == "discount":
        state["discount_pct"] = min(0.6, state.get("discount_pct", 0.0) + value)


def pick_indices(num_options, pick_count):

    if num_options == 0:
        return []
    pick_count = min(pick_count, num_options)
    raw = input(f"Pick {pick_count} card number(s) separated by spaces: ")
    return validate_pack_picks(raw, num_options, pick_count)


def open_booster_pack(pack, state, max_slots):

    if pack["kind"] == "Buffoon":
        owned_ids = [j["id"] for j in state["jokers"]]
        available = [j for j in JOKER_POOL if j["id"] not in owned_ids]
        options = random.sample(available, min(pack["offer_count"], len(available)))

        if not options:
            show_shop_message("No new Jokers left to offer.")
            return

        labels = [f"{j['name']} - {j['desc']}" for j in options]
        show_pack_options(pack["name"], labels, pack["pick_count"])

        for i in pick_indices(len(options), pack["pick_count"]):
            joker = options[i]
            if len(state["jokers"]) >= max_slots:
                show_shop_message(f"No free Joker slot - skipped {joker['name']}.")
                continue
            state["jokers"].append(dict(joker))
            show_shop_message(f"Added {joker['name']} to your Jokers!")

    elif pack["kind"] == "Celestial":
        options = [random.choice(CELESTIAL_POOL) for _ in range(pack["offer_count"])]
        labels = [f"{p['name']} - upgrades {p['hand_type']}" for p in options]
        show_pack_options(pack["name"], labels, pack["pick_count"])

        for i in pick_indices(len(options), pack["pick_count"]):
            planet = options[i]
            hand_type = planet["hand_type"]
            state["hand_levels"][hand_type] = state["hand_levels"].get(hand_type, 1) + 1
            show_shop_message(f"{planet['name']} used! {hand_type} is now level {state['hand_levels'][hand_type]}.")

    elif pack["kind"] == "Standard":
        options = [make_enhanced_card() for _ in range(pack["offer_count"])]
        labels = [c.describe() for c in options]
        show_pack_options(pack["name"], labels, pack["pick_count"])

        for i in pick_indices(len(options), pack["pick_count"]):
            card = options[i]
            state["master_cards"].append(card)
            show_shop_message(f"Added {card.describe()} to your deck!")


def buy_entry(entry, shop, state, max_slots):

    cost = entry["cost"]

    if state["money"] < cost:
        show_shop_message("Not enough money for that.")
        return

    if entry["section"] == "card":
        slot = entry["data"]

        if slot["kind"] == "joker":
            if len(state["jokers"]) >= max_slots:
                show_shop_message("You don't have any free Joker slots.")
                return
            state["money"] -= cost
            joker_record = {k: v for k, v in slot.items() if k != "kind"}
            joker_record["cost"] = cost  # what was actually paid, after any discount/Tag
            state["jokers"].append(joker_record)

            if entry["granted"]:
                shop.granted_slots[entry["slot_index"]] = None
            else:
                shop.card_slots[entry["slot_index"]] = None

            if slot.get("tag_bonus"):
                show_shop_message(f"Claimed {slot['name']} with a {tag_bonus_desc(slot['tag_bonus'])} bonus!")
            else:
                show_shop_message(f"{'Claimed' if cost == 0 else 'Bought'} {slot['name']}!")

        else:
            state["money"] -= cost
            hand_type = slot["hand_type"]
            state["hand_levels"][hand_type] = state["hand_levels"].get(hand_type, 1) + 1

            if entry["granted"]:
                shop.granted_slots[entry["slot_index"]] = None
            else:
                shop.card_slots[entry["slot_index"]] = None

            show_shop_message(f"Used {slot['name']}! {hand_type} is now level {state['hand_levels'][hand_type]}.")

    elif entry["section"] == "pack":
        slot = entry["data"]
        state["money"] -= cost
        shop.booster_slots[entry["slot_index"]] = None
        open_booster_pack(slot, state, max_slots)

    elif entry["section"] == "voucher":
        state["money"] -= cost
        voucher = entry["data"]
        apply_voucher_effect(voucher, state)
        state["vouchers"].append(voucher["id"])
        show_shop_message(f"Bought {voucher['name']}!")
        shop.voucher_slots[entry["slot_index"]] = None


def joker_sell_price(bought_cost):

    if bought_cost <= 4:
        return 1
    elif bought_cost <= 8:
        return 2
    else:
        return 3


def handle_sell(state):

    if not state["jokers"]:
        show_shop_message("You don't own any Jokers to sell.")
        return

    labels = [f"{j['name']} - sell for ${joker_sell_price(j.get('cost', 4))}" for j in state["jokers"]]
    show_pack_options("Sell a Joker", labels, 1)

    raw = input("Joker number to sell, or 0 to cancel: ")
    result = validate_sell_choice(raw, len(state["jokers"]))

    if result == "cancel":
        return

    joker = state["jokers"].pop(result)
    price = joker_sell_price(joker.get("cost", 4))
    state["money"] += price
    show_shop_message(f"Sold {joker['name']} for ${price}.")


def handle_destroy(state):

    if state["money"] < DESTROY_COST:
        show_shop_message(f"Not enough money to destroy a card (${DESTROY_COST} needed).")
        return

    show_destroy_prompt()
    raw = input("Card to destroy (rank suit), or 0 to cancel: ")
    result = validate_destroy_input(raw)

    if result == "cancel":
        return

    rank, suit = result
    matches = [c for c in state["master_cards"] if c.rank == rank and c.suit == suit]

    if not matches:
        show_shop_message("You don't have that card.")
        return

    if len(matches) == 1:
        chosen = matches[0]
    else:
        labels = [c.describe() for c in matches]
        show_pack_options("Multiple matches - pick one to destroy", labels, 1)
        idx = pick_indices(len(matches), 1)
        chosen = matches[idx[0]]

    state["money"] -= DESTROY_COST
    state["master_cards"].remove(chosen)
    show_shop_message(f"Destroyed {chosen.describe()}.")


def run_shop(state, after_boss=False):

    pending_joker_grants = state.pop("pending_joker_grants", [])
    extra_voucher = state.pop("extra_voucher_tag", False)
    free_items = state.pop("free_shop_tag", False)
    cheap_reroll = state.pop("cheap_reroll_tag", False)

    shop = Shop(owned_joker_ids=[j["id"] for j in state["jokers"]],
                after_boss=after_boss,
                owned_voucher_ids=state["vouchers"],
                discount_pct=state.get("discount_pct", 0.0),
                pending_joker_grants=pending_joker_grants,
                extra_voucher=extra_voucher,
                free_items=free_items)

    reroll_base = 0 if cheap_reroll else BASE_REROLL_COST
    reroll_floor = 0 if cheap_reroll else 1

    while True:
        
        shop.discount_pct = state.get("discount_pct", 0.0)
        max_slots = JOKER_SLOTS + state["bonus_joker_slots"]
        reroll_cost = max(reroll_floor, reroll_base + shop.reroll_count - state.get("reroll_discount", 0))

        entries = shop.build_entries()

        show_owned_jokers(state["jokers"])
        show_shop(state["money"], entries, max_slots, len(state["jokers"]), reroll_cost, DESTROY_COST)

        choice = input("Choice: ")
        choice = validate_shop_choice(choice, len(entries))

        if choice == "leave":
            break

        elif choice == "reroll":
            if state["money"] < reroll_cost:
                show_shop_message(f"Not enough money to reroll (${reroll_cost} needed).")
            else:
                state["money"] -= reroll_cost
                shop.reroll()
                show_shop_message("Shop rerolled!")

        elif choice == "destroy":
            handle_destroy(state)

        elif choice == "sell":
            handle_sell(state)

        else:
            entry = next(e for e in entries if e["number"] == choice)
            buy_entry(entry, shop, state, max_slots)

    return state