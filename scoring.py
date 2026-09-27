import math
from card import Card

# Base chips/mult for each hand at level 1, and how much each is boosted by
# every Planet-card level-up.
HAND_INFO = {
    "Flush Five":       {"chips": 160, "mult": 16, "chip_step": 50, "mult_step": 3},
    "Flush House":      {"chips": 140, "mult": 14, "chip_step": 40, "mult_step": 4},
    "Five of a Kind":   {"chips": 120, "mult": 12, "chip_step": 35, "mult_step": 3},
    "Straight Flush":   {"chips": 100, "mult": 8,  "chip_step": 40, "mult_step": 4},
    "Four of a Kind":   {"chips": 60,  "mult": 7,  "chip_step": 30, "mult_step": 3},
    "Full House":       {"chips": 40,  "mult": 4,  "chip_step": 25, "mult_step": 2},
    "Flush":            {"chips": 35,  "mult": 4,  "chip_step": 15, "mult_step": 2},
    "Straight":         {"chips": 30,  "mult": 4,  "chip_step": 30, "mult_step": 3},
    "Three of a Kind":  {"chips": 30,  "mult": 3,  "chip_step": 20, "mult_step": 2},
    "Two Pair":         {"chips": 20,  "mult": 2,  "chip_step": 20, "mult_step": 1},
    "One Pair":         {"chips": 10,  "mult": 2,  "chip_step": 15, "mult_step": 1},
    "High Card":        {"chips": 5,   "mult": 1,  "chip_step": 10, "mult_step": 1},
}


def calc_score(hand, hand_type, jokers=None, hand_levels=None,
                discards_remaining=0, remaining_cards=0, money=0):
    jokers = jokers or []
    hand_levels = hand_levels or {}

    info = HAND_INFO[hand_type]
    level = hand_levels.get(hand_type, 1)

    chips = info["chips"] + info["chip_step"] * (level - 1)
    mult = info["mult"] + info["mult_step"] * (level - 1)

    for card in hand:
        chips += card.get_value()
        mult += getattr(card, "bonus_mult", 0)

    # ------------------------------------------------------------------
    # Joker effects
    # ------------------------------------------------------------------
    suits_in_hand = [card.suit for card in hand]
    ranks_in_hand = [card.rank for card in hand]
    face_ranks = {"J", "Q", "K"}
    has_face_card = any(rank in face_ranks for rank in ranks_in_hand)

    xmult_multiplier = 1.0

    for joker in jokers:
        j_type = joker["type"]
        value = joker["value"]

        if j_type == "chips":
            chips += value
        elif j_type == "mult":
            mult += value
        elif j_type == "xmult":
            xmult_multiplier *= value
        elif j_type == "chips_hand" and hand_type in joker.get("hands", []):
            chips += value
        elif j_type == "mult_hand" and hand_type in joker.get("hands", []):
            mult += value
        elif j_type == "xmult_hand" and hand_type in joker.get("hands", []):
            xmult_multiplier *= value
        elif j_type == "chips_suit":
            chips += value * suits_in_hand.count(joker.get("suit"))
        elif j_type == "mult_suit":
            mult += value * suits_in_hand.count(joker.get("suit"))
        elif j_type == "chips_per_facecard":
            chips += value * sum(1 for rank in ranks_in_hand if rank in face_ranks)
        elif j_type == "xmult_if_facecard" and has_face_card:
            xmult_multiplier *= value
        elif j_type == "chips_per_rank":
            chips += value * ranks_in_hand.count(joker.get("rank"))
        elif j_type == "chips_per_discard_remaining":
            chips += value * discards_remaining
        elif j_type == "chips_per_deck_card":
            chips += value * remaining_cards
        elif j_type == "chips_per_dollar":
            chips += value * money

        tag_bonus = joker.get("tag_bonus")
        if tag_bonus:
            if tag_bonus["type"] == "chips":
                chips += tag_bonus["value"]
            elif tag_bonus["type"] == "mult":
                mult += tag_bonus["value"]
            elif tag_bonus["type"] == "xmult":
                xmult_multiplier *= tag_bonus["value"]

    mult *= xmult_multiplier
    score = chips * mult

    return int(score)


def target_score(ante, difficulty, blind, boss_mult=2):

    if difficulty == "White":
        if ante == 1:
            a = 300
        elif ante == 2:
            a = 800
        elif ante == 3:
            a = 2800
        elif ante == 4:
            a = 6000
        elif ante == 5:
            a = 11000
        elif ante == 6:
            a = 20000
        elif ante == 7:
            a = 35000
        elif ante == 8:
            a = 50000
        else:
            a = 50000
            b = 1.6
            c = ante - 8
            d = 1 + (0.2 * c)
            k = 0.75
            base_score = (a * (b + (((k * c) ** d)**c)))
            magnitude = 10 ** (math.floor(math.log10(base_score)) - 2)
            rounded_score = math.floor(base_score / magnitude) * magnitude
            a = rounded_score

    elif difficulty == "Black":
        if ante == 1:
            a = 300
        elif ante == 2:
            a = 900
        elif ante == 3:
            a = 3200
        elif ante == 4:
            a = 9000
        elif ante == 5:
            a = 18000
        elif ante == 6:
            a = 32000
        elif ante == 7:
            a = 56000
        elif ante == 8:
            a = 90000
        else:
            a = 90000
            b = 1.6
            c = ante - 8
            d = 1 + (0.2 * c)
            k = 1.0
            base_score = (a * (b + (((k * c) ** d)**c)))
            magnitude = 10 ** (math.floor(math.log10(base_score)) - 2)
            rounded_score = math.floor(base_score / magnitude) * magnitude
            a = rounded_score

    else:
        if ante == 1:
            a = 300
        elif ante == 2:
            a = 1000
        elif ante == 3:
            a = 3600
        elif ante == 4:
            a = 10000
        elif ante == 5:
            a = 25000
        elif ante == 6:
            a = 50000
        elif ante == 7:
            a = 90000
        elif ante == 8:
            a = 180000
        else:
            a = 180000
            b = 1.6
            c = ante - 8
            d = 1 + (0.2 * c)
            k = 1.0
            base_score = (a * (b + (((k * c) ** d)**c)))
            magnitude = 10 ** (math.floor(math.log10(base_score)) - 2)
            rounded_score = math.floor(base_score / magnitude) * magnitude
            a = rounded_score

    if blind == "Small Blind":
        a = a * 1
    elif blind == "Big Blind":
        a = a * 1.5
    elif blind == "Boss Blind":
        a = a * boss_mult

    return int(a)