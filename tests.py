"""
Test suite for the poker game.

Run all tests with:
    python3 -m unittest tests -v
or simply:
    python3 tests.py
"""

import unittest
from unittest.mock import patch

from card import Card, Deck, RANKS, SUITS
from poker import evaluate_hand
from scoring import calc_score, target_score, HAND_INFO
import shop
import tags
import input_validation as iv
import main

def make_state(**overrides):

    state = {
        "money": 20,
        "jokers": [],
        "vouchers": [],
        "hand_levels": {},
        "master_cards": [],
        "bonus_hand_size": 0,
        "bonus_hands": 0,
        "bonus_discards": 0,
        "bonus_interest_cap": 0,
        "bonus_joker_slots": 0,
        "reroll_discount": 0,
        "discount_pct": 0.0,
        "boss_effect": None,
        "investment_bonus": 0,
    }
    state.update(overrides)
    return state


def make_hand(specs):

    values = {rank: i + 2 for i, rank in enumerate(RANKS)}
    return [Card(rank, suit, values[rank]) for rank, suit in specs]


# ---------------------------------------------------------------------------
# card.py
# ---------------------------------------------------------------------------

class TestCard(unittest.TestCase):

    def test_get_value_plain(self):
        card = Card("9", "♦", 9)
        self.assertEqual(card.get_value(), 9)

    def test_get_value_with_bonus_chips(self):
        card = Card("9", "♦", 9, enhancement="bonus", bonus_chips=30)
        self.assertEqual(card.get_value(), 39)

    def test_show_card_plain(self):
        self.assertEqual(Card("K", "♠", 13).show_card(), "K♠")

    def test_show_card_bonus_suffix(self):
        card = Card("K", "♠", 13, enhancement="bonus", bonus_chips=30)
        self.assertEqual(card.show_card(), "K♠c")

    def test_show_card_mult_suffix(self):
        card = Card("K", "♠", 13, enhancement="mult", bonus_mult=4)
        self.assertEqual(card.show_card(), "K♠m")

    def test_describe_plain(self):
        self.assertEqual(Card("2", "♣", 2).describe(), "2♣")

    def test_describe_bonus(self):
        card = Card("2", "♣", 2, enhancement="bonus", bonus_chips=30)
        self.assertIn("Bonus Card: +30 Chips", card.describe())

    def test_describe_mult(self):
        card = Card("2", "♣", 2, enhancement="mult", bonus_mult=4)
        self.assertIn("Mult Card: +4 Mult", card.describe())


class TestDeck(unittest.TestCase):

    def test_build_deck_has_52_unique_cards(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)
        combos = {(c.rank, c.suit) for c in deck.cards}
        self.assertEqual(len(combos), 52)

    def test_shuffle_preserves_composition(self):
        deck = Deck()
        before = sorted((c.rank, c.suit) for c in deck.cards)
        deck.shuffle()
        after = sorted((c.rank, c.suit) for c in deck.cards)
        self.assertEqual(before, after)

    def test_deal_card_reduces_deck(self):
        deck = Deck()
        dealt, remaining = deck.deal_card(5)
        self.assertEqual(len(dealt), 5)
        self.assertEqual(remaining, 47)
        self.assertEqual(len(deck.cards), 47)

    def test_deal_more_than_available_caps_at_deck_size(self):
        deck = Deck()
        deck.cards = deck.cards[:3]
        dealt, remaining = deck.deal_card(10)
        self.assertEqual(len(dealt), 3)
        self.assertEqual(remaining, 0)

    def test_choose_card_found(self):
        deck = Deck()
        card = deck.choose_card("A", "♠")
        self.assertIsNotNone(card)
        self.assertEqual((card.rank, card.suit), ("A", "♠"))
        self.assertEqual(len(deck.cards), 51)

    def test_choose_card_not_found(self):
        deck = Deck()
        deck.cards = []
        self.assertIsNone(deck.choose_card("A", "♠"))


# ---------------------------------------------------------------------------
# poker.py - evaluate_hand
# ---------------------------------------------------------------------------

class TestEvaluateHand(unittest.TestCase):

    def test_flush_five(self):
        hand = make_hand([("A", "♣")] * 5)
        self.assertEqual(evaluate_hand(hand), "Flush Five")

    def test_flush_house(self):
        hand = make_hand([("A", "♣"), ("A", "♣"), ("A", "♣"), ("K", "♣"), ("K", "♣")])
        self.assertEqual(evaluate_hand(hand), "Flush House")

    def test_five_of_a_kind(self):
        hand = make_hand([("A", "♣"), ("A", "♦"), ("A", "♠"), ("A", "♥"), ("A", "♣")])
        self.assertEqual(evaluate_hand(hand), "Five of a Kind")

    def test_straight_flush(self):
        hand = make_hand([("A", "♣"), ("K", "♣"), ("Q", "♣"), ("J", "♣"), ("10", "♣")])
        self.assertEqual(evaluate_hand(hand), "Straight Flush")

    def test_flush(self):
        hand = make_hand([("A", "♣"), ("K", "♣"), ("Q", "♣"), ("J", "♣"), ("9", "♣")])
        self.assertEqual(evaluate_hand(hand), "Flush")

    def test_straight(self):
        hand = make_hand([("A", "♣"), ("K", "♦"), ("Q", "♠"), ("J", "♥"), ("10", "♣")])
        self.assertEqual(evaluate_hand(hand), "Straight")

    def test_ace_low_straight(self):
        hand = make_hand([("A", "♣"), ("2", "♦"), ("3", "♠"), ("4", "♥"), ("5", "♣")])
        self.assertEqual(evaluate_hand(hand), "Straight")

    def test_full_house(self):
        hand = make_hand([("A", "♣"), ("A", "♦"), ("A", "♠"), ("K", "♥"), ("K", "♣")])
        self.assertEqual(evaluate_hand(hand), "Full House")

    def test_four_of_a_kind(self):
        hand = make_hand([("A", "♣"), ("A", "♦"), ("A", "♠"), ("A", "♥"), ("K", "♣")])
        self.assertEqual(evaluate_hand(hand), "Four of a Kind")

    def test_three_of_a_kind(self):
        hand = make_hand([("A", "♣"), ("A", "♦"), ("A", "♠"), ("K", "♥"), ("Q", "♣")])
        self.assertEqual(evaluate_hand(hand), "Three of a Kind")

    def test_two_pair(self):
        hand = make_hand([("A", "♣"), ("A", "♦"), ("K", "♠"), ("K", "♥"), ("Q", "♣")])
        self.assertEqual(evaluate_hand(hand), "Two Pair")

    def test_one_pair(self):
        hand = make_hand([("A", "♣"), ("A", "♦"), ("K", "♠"), ("Q", "♥"), ("J", "♣")])
        self.assertEqual(evaluate_hand(hand), "One Pair")

    def test_high_card(self):
        hand = make_hand([("A", "♣"), ("K", "♦"), ("Q", "♠"), ("J", "♥"), ("9", "♣")])
        self.assertEqual(evaluate_hand(hand), "High Card")

    def test_four_of_a_kind_fewer_than_5_cards(self):
        # Duplicate-based hands work below 5 cards too (only the 5-card-only
        # combos like Flush/Straight require exactly 5).
        hand = make_hand([("A", "♣"), ("A", "♦"), ("A", "♠"), ("A", "♥")])
        self.assertEqual(evaluate_hand(hand), "Four of a Kind")

    def test_not_a_flush_when_five_cards_mixed_suits_no_pair(self):
        hand = make_hand([("A", "♣"), ("K", "♦"), ("8", "♠"), ("5", "♥"), ("2", "♣")])
        self.assertEqual(evaluate_hand(hand), "High Card")


# ---------------------------------------------------------------------------
# scoring.py
# ---------------------------------------------------------------------------

class TestCalcScore(unittest.TestCase):

    def test_high_card_no_joker(self):
        hand = make_hand([("2", "♠"), ("5", "♥"), ("9", "♦"), ("K", "♣"), ("A", "♠")])
        # base: chips=5+mult=1 at level 1; card values 2+5+9+13+14=43
        expected_chips = HAND_INFO["High Card"]["chips"] + 43
        expected = expected_chips * HAND_INFO["High Card"]["mult"]
        self.assertEqual(calc_score(hand, "High Card"), expected)

    def test_hand_level_increases_score(self):
        hand = make_hand([("2", "♠"), ("3", "♥")])
        level1 = calc_score(hand, "One Pair", hand_levels={"One Pair": 1})
        level2 = calc_score(hand, "One Pair", hand_levels={"One Pair": 2})
        self.assertGreater(level2, level1)

    def test_flat_mult_joker(self):
        hand = make_hand([("2", "♠"), ("3", "♥")])
        joker = {"type": "mult", "value": 4}
        base = calc_score(hand, "High Card")
        boosted = calc_score(hand, "High Card", jokers=[joker])
        self.assertGreater(boosted, base)

    def test_xmult_joker_multiplies(self):
        hand = make_hand([("2", "♠"), ("3", "♥")])
        joker = {"type": "xmult", "value": 2.0}
        base = calc_score(hand, "High Card")
        boosted = calc_score(hand, "High Card", jokers=[joker])
        self.assertEqual(boosted, base * 2)

    def test_chips_per_dollar_joker(self):
        hand = make_hand([("2", "♠"), ("3", "♥")])
        joker = {"type": "chips_per_dollar", "value": 2}
        no_money = calc_score(hand, "High Card", jokers=[joker], money=0)
        with_money = calc_score(hand, "High Card", jokers=[joker], money=10)
        self.assertEqual(with_money - no_money, 20)  # 2 chips * 10 money, mult stays 1

    def test_tag_bonus_chips(self):
        hand = make_hand([("2", "♠"), ("3", "♥")])
        joker = {"type": "mult_suit", "value": 1, "suit": "♦", "tag_bonus": {"type": "chips", "value": 50}}
        base = calc_score(hand, "High Card")
        boosted = calc_score(hand, "High Card", jokers=[joker])
        self.assertEqual(boosted - base, 50)  # mult_suit contributes 0 (no ♦ in hand)

    def test_bonus_mult_card_adds_mult(self):
        hand = make_hand([("2", "♠")])
        hand[0].bonus_mult = 4
        boosted = calc_score(hand, "High Card")
        plain_hand = make_hand([("2", "♠")])
        base = calc_score(plain_hand, "High Card")
        self.assertGreater(boosted, base)


class TestTargetScore(unittest.TestCase):

    def test_white_ante1_small_blind(self):
        self.assertEqual(target_score(1, "White", "Small Blind"), 30)

    def test_big_blind_is_1point5x_small(self):
        small = target_score(1, "White", "Small Blind")
        big = target_score(1, "White", "Big Blind")
        self.assertEqual(big, int(small * 1.5))

    def test_boss_blind_default_2x(self):
        small = target_score(1, "White", "Small Blind")
        boss = target_score(1, "White", "Boss Blind")
        self.assertEqual(boss, small * 2)

    def test_boss_blind_custom_mult(self):
        small = target_score(1, "White", "Small Blind")
        boss = target_score(1, "White", "Boss Blind", boss_mult=1.6)
        self.assertEqual(boss, int(small * 1.6))

    def test_targets_increase_with_ante(self):
        t1 = target_score(1, "White", "Small Blind")
        t2 = target_score(2, "White", "Small Blind")
        t8 = target_score(8, "White", "Small Blind")
        t9 = target_score(9, "White", "Small Blind")
        self.assertLess(t1, t2)
        self.assertLess(t2, t8)
        self.assertLess(t8, t9)  # formula-based scaling beyond ante 8

    def test_harder_difficulties_have_higher_targets(self):
        # Black and Gold happen to tie at ante 1 (both 300 by design);
        # they diverge from ante 2 onward, so compare there instead.
        white = target_score(2, "White", "Small Blind")
        black = target_score(2, "Black", "Small Blind")
        gold = target_score(2, "Gold", "Small Blind")
        self.assertLess(white, black)
        self.assertLess(black, gold)


# ---------------------------------------------------------------------------
# shop.py
# ---------------------------------------------------------------------------

class TestJokerSellPrice(unittest.TestCase):

    def test_cheap_joker_sells_for_1(self):
        self.assertEqual(shop.joker_sell_price(3), 1)
        self.assertEqual(shop.joker_sell_price(4), 1)

    def test_mid_joker_sells_for_2(self):
        self.assertEqual(shop.joker_sell_price(5), 2)
        self.assertEqual(shop.joker_sell_price(8), 2)

    def test_expensive_joker_sells_for_3(self):
        self.assertEqual(shop.joker_sell_price(9), 3)
        self.assertEqual(shop.joker_sell_price(14), 3)


class TestApplyVoucherEffect(unittest.TestCase):

    def test_hand_size_perm(self):
        state = make_state()
        shop.apply_voucher_effect({"type": "hand_size_perm", "value": 1}, state)
        self.assertEqual(state["bonus_hand_size"], 1)

    def test_hands_perm(self):
        state = make_state()
        shop.apply_voucher_effect({"type": "hands_perm", "value": 1}, state)
        self.assertEqual(state["bonus_hands"], 1)

    def test_discards_perm(self):
        state = make_state()
        shop.apply_voucher_effect({"type": "discards_perm", "value": 1}, state)
        self.assertEqual(state["bonus_discards"], 1)

    def test_interest_cap_perm(self):
        state = make_state()
        shop.apply_voucher_effect({"type": "interest_cap_perm", "value": 5}, state)
        self.assertEqual(state["bonus_interest_cap"], 5)

    def test_joker_slot_perm(self):
        state = make_state()
        shop.apply_voucher_effect({"type": "joker_slot_perm", "value": 1}, state)
        self.assertEqual(state["bonus_joker_slots"], 1)

    def test_reroll_discount_stacks(self):
        state = make_state()
        shop.apply_voucher_effect({"type": "reroll_discount", "value": 2}, state)
        shop.apply_voucher_effect({"type": "reroll_discount", "value": 2}, state)
        self.assertEqual(state["reroll_discount"], 4)

    def test_discount_caps_at_0_6(self):
        state = make_state()
        for _ in range(5):
            shop.apply_voucher_effect({"type": "discount", "value": 0.2}, state)
        self.assertEqual(state["discount_pct"], 0.6)


class TestShopPricing(unittest.TestCase):

    def test_zero_cost_is_free(self):
        s = shop.Shop(owned_joker_ids=[], after_boss=False, owned_voucher_ids=[])
        self.assertEqual(s.price(0), 0)

    def test_no_discount_passthrough(self):
        s = shop.Shop(owned_joker_ids=[], after_boss=False, owned_voucher_ids=[])
        self.assertEqual(s.price(4), 4)

    def test_discount_rounds_and_floors_at_1(self):
        s = shop.Shop(owned_joker_ids=[], after_boss=False, owned_voucher_ids=[], discount_pct=0.9)
        self.assertEqual(s.price(4), 1)  # would round to 0, floored to 1


class TestShopSlots(unittest.TestCase):

    def test_card_slots_always_two_valid_kinds(self):
        for _ in range(20):
            slots = shop.make_card_slots(owned_joker_ids=[])
            self.assertEqual(len(slots), 2)
            for slot in slots:
                self.assertIn(slot["kind"], ("joker", "planet"))

    def test_make_joker_offer_excludes_owned(self):
        all_ids = [j["id"] for j in shop.JOKER_POOL]
        owned = all_ids[:-1]  # own everything except the last one
        offer = shop.make_joker_offer(owned)
        self.assertEqual(offer["id"], all_ids[-1])

    def test_make_joker_offer_none_when_all_owned(self):
        all_ids = [j["id"] for j in shop.JOKER_POOL]
        self.assertIsNone(shop.make_joker_offer(all_ids))

    def test_granted_joker_offer_matches_rarity(self):
        offer = shop.make_granted_joker_offer([], "Rare")
        self.assertEqual(offer["rarity"], "Rare")

    def test_granted_joker_offer_falls_back_when_rarity_exhausted(self):
        rare_ids = [j["id"] for j in shop.JOKER_POOL if j["rarity"] == "Rare"]
        legendary_ids = [j["id"] for j in shop.JOKER_POOL if j["rarity"] == "Legendary"]
        owned = rare_ids + legendary_ids
        # Ask for a rarity ("Rare") that's fully owned/excluded - should fall back.
        offer = shop.make_granted_joker_offer(owned, "Rare")
        self.assertIsNotNone(offer)
        self.assertNotIn(offer["id"], owned)

    def test_voucher_slots_after_boss(self):
        s = shop.Shop(owned_joker_ids=[], after_boss=True, owned_voucher_ids=[])
        self.assertEqual(len(s.voucher_slots), 1)

    def test_voucher_slots_extra_tag_without_after_boss(self):
        s = shop.Shop(owned_joker_ids=[], after_boss=False, owned_voucher_ids=[], extra_voucher=True)
        self.assertEqual(len(s.voucher_slots), 1)

    def test_voucher_slots_stack(self):
        s = shop.Shop(owned_joker_ids=[], after_boss=True, owned_voucher_ids=[], extra_voucher=True)
        self.assertEqual(len(s.voucher_slots), 2)

    def test_granted_slots_carry_tag_bonus(self):
        grants = [{"rarity": "Common", "tag_bonus": {"type": "chips", "value": 50}}]
        s = shop.Shop(owned_joker_ids=[], after_boss=False, owned_voucher_ids=[],
                       pending_joker_grants=grants)
        self.assertEqual(len(s.granted_slots), 1)
        self.assertEqual(s.granted_slots[0]["tag_bonus"], {"type": "chips", "value": 50})

    def test_reroll_increments_count_and_clears_free_items(self):
        s = shop.Shop(owned_joker_ids=[], after_boss=False, owned_voucher_ids=[], free_items=True)
        self.assertTrue(s.free_items)
        s.reroll()
        self.assertEqual(s.reroll_count, 1)
        self.assertFalse(s.free_items)


class TestBuyEntry(unittest.TestCase):

    def test_buying_joker_deducts_money_and_adds_joker(self):
        state = make_state(money=10)
        s = shop.Shop(owned_joker_ids=[], after_boss=False, owned_voucher_ids=[])
        s.card_slots = [shop.make_joker_offer([]), shop.make_planet_offer()]
        entries = s.build_entries()
        card_entry = next(e for e in entries if e["section"] == "card" and e["data"]["kind"] == "joker")
        cost = card_entry["cost"]
        shop.buy_entry(card_entry, s, state, max_slots=5)
        self.assertEqual(state["money"], 10 - cost)
        self.assertEqual(len(state["jokers"]), 1)

    def test_buying_joker_refused_when_slots_full(self):
        state = make_state(money=100, jokers=[{"id": "x", "name": "X", "type": "mult", "value": 1, "desc": "", "cost": 1}])
        s = shop.Shop(owned_joker_ids=[], after_boss=False, owned_voucher_ids=[])
        s.card_slots = [shop.make_joker_offer([]), shop.make_planet_offer()]
        entries = s.build_entries()
        card_entry = next(e for e in entries if e["section"] == "card" and e["data"]["kind"] == "joker")
        shop.buy_entry(card_entry, s, state, max_slots=1)  # already at cap
        self.assertEqual(len(state["jokers"]), 1)  # unchanged
        self.assertEqual(state["money"], 100)  # nothing spent

    def test_buying_planet_levels_up_hand(self):
        state = make_state(money=10)
        s = shop.Shop(owned_joker_ids=[], after_boss=False, owned_voucher_ids=[])
        # Force a planet-only shop for a deterministic entry.
        s.card_slots = [shop.make_planet_offer(), shop.make_planet_offer()]
        entries = s.build_entries()
        planet_entry = next(e for e in entries if e["data"]["kind"] == "planet")
        hand_type = planet_entry["data"]["hand_type"]
        shop.buy_entry(planet_entry, s, state, max_slots=5)
        self.assertEqual(state["hand_levels"][hand_type], 2)

    def test_not_enough_money_refuses_purchase(self):
        state = make_state(money=0)
        s = shop.Shop(owned_joker_ids=[], after_boss=False, owned_voucher_ids=[])
        s.card_slots = [shop.make_planet_offer(), shop.make_planet_offer()]
        entries = s.build_entries()
        planet_entry = entries[0]
        shop.buy_entry(planet_entry, s, state, max_slots=5)
        self.assertEqual(state["hand_levels"], {})
        self.assertEqual(state["money"], 0)


class TestHandleSellAndDestroy(unittest.TestCase):

    def test_handle_sell_removes_joker_and_pays_out(self):
        state = make_state(money=0, jokers=[
            {"id": "j_flat_mult", "name": "Joker", "type": "mult", "value": 4, "desc": "+4 Mult", "cost": 3},
        ])
        with patch("builtins.input", return_value="1"):
            shop.handle_sell(state)
        self.assertEqual(state["jokers"], [])
        self.assertEqual(state["money"], 1)  # cost 3 -> sells for $1

    def test_handle_sell_cancel_keeps_joker(self):
        joker = {"id": "j_flat_mult", "name": "Joker", "type": "mult", "value": 4, "desc": "+4 Mult", "cost": 3}
        state = make_state(money=0, jokers=[joker])
        with patch("builtins.input", return_value="0"):
            shop.handle_sell(state)
        self.assertEqual(state["jokers"], [joker])

    def test_handle_destroy_removes_matching_card(self):
        target = Card("9", "♦", 9)
        state = make_state(money=10, master_cards=[target, Card("2", "♠", 2)])
        with patch("builtins.input", return_value="9 ♦"):
            shop.handle_destroy(state)
        self.assertEqual(len(state["master_cards"]), 1)
        self.assertNotIn(target, state["master_cards"])
        self.assertEqual(state["money"], 10 - shop.DESTROY_COST)

    def test_handle_destroy_not_enough_money(self):
        target = Card("9", "♦", 9)
        state = make_state(money=0, master_cards=[target])
        shop.handle_destroy(state)  # should return early, no input() call needed
        self.assertEqual(len(state["master_cards"]), 1)


# ---------------------------------------------------------------------------
# tags.py
# ---------------------------------------------------------------------------

def get_tag(tag_id):
    return next(t for t in tags.TAG_POOL if t["id"] == tag_id)


def forced_tag_choice(forced_tag):
    """A random.choice replacement that only intercepts TAG_POOL selection,
    letting every other random.choice call (inside award_random_tag's
    effects) behave normally."""
    import random as _random
    real_choice = _random.choice

    def _choice(seq):
        if seq is tags.TAG_POOL:
            return forced_tag
        return real_choice(seq)
    return _choice


class TestTagPool(unittest.TestCase):

    def test_sixteen_unique_tags(self):
        self.assertEqual(len(tags.TAG_POOL), 16)
        ids = [t["id"] for t in tags.TAG_POOL]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_tag_has_name_and_desc(self):
        for tag in tags.TAG_POOL:
            self.assertTrue(tag["name"])
            self.assertTrue(tag["desc"])


class TestPickBossEffect(unittest.TestCase):

    def test_returns_a_boss_effect(self):
        effect = tags.pick_boss_effect()
        self.assertIn(effect, tags.BOSS_EFFECTS)

    def test_avoids_repeating_current_when_possible(self):
        current = tags.BOSS_EFFECTS[0]
        for _ in range(20):
            new_effect = tags.pick_boss_effect(current)
            self.assertNotEqual(new_effect["id"], current["id"])


class TestAwardRandomTag(unittest.TestCase):

    def test_economy_tag_doubles_money(self):
        state = make_state(money=30)
        with patch("random.choice", forced_tag_choice(get_tag("economy"))):
            tags.award_random_tag(state, max_slots=5)
        self.assertEqual(state["money"], 60)

    def test_economy_tag_capped_at_40(self):
        state = make_state(money=100)
        with patch("random.choice", forced_tag_choice(get_tag("economy"))):
            tags.award_random_tag(state, max_slots=5)
        self.assertEqual(state["money"], 140)

    def test_orbital_tag_adds_3_levels(self):
        state = make_state()
        with patch("random.choice", forced_tag_choice(get_tag("orbital"))):
            tags.award_random_tag(state, max_slots=5)
        self.assertEqual(len(state["hand_levels"]), 1)
        self.assertEqual(list(state["hand_levels"].values())[0], 4)

    def test_juggle_tag_returns_gain(self):
        state = make_state()
        with patch("random.choice", forced_tag_choice(get_tag("juggle"))):
            result = tags.award_random_tag(state, max_slots=5)
        self.assertEqual(result["juggle_gain"], 3)

    def test_boss_tag_sets_boss_effect(self):
        state = make_state()
        with patch("random.choice", forced_tag_choice(get_tag("boss"))):
            tags.award_random_tag(state, max_slots=5)
        self.assertIsNotNone(state["boss_effect"])

    def test_investment_tag_queues_money(self):
        state = make_state()
        with patch("random.choice", forced_tag_choice(get_tag("investment"))):
            tags.award_random_tag(state, max_slots=5)
        self.assertEqual(state["investment_bonus"], 25)

    def test_investment_tag_stacks(self):
        state = make_state()
        with patch("random.choice", forced_tag_choice(get_tag("investment"))):
            tags.award_random_tag(state, max_slots=5)
            tags.award_random_tag(state, max_slots=5)
        self.assertEqual(state["investment_bonus"], 50)

    def test_uncommon_tag_queues_joker_grant(self):
        state = make_state()
        with patch("random.choice", forced_tag_choice(get_tag("uncommon"))):
            tags.award_random_tag(state, max_slots=5)
        self.assertEqual(state["pending_joker_grants"], [{"rarity": "Uncommon", "tag_bonus": None}])

    def test_chip_tag_queues_common_bonus(self):
        state = make_state()
        with patch("random.choice", forced_tag_choice(get_tag("chip"))):
            tags.award_random_tag(state, max_slots=5)
        self.assertEqual(state["pending_joker_grants"],
                          [{"rarity": "Common", "tag_bonus": {"type": "chips", "value": 50}}])

    def test_coupon_tag_sets_flag(self):
        state = make_state()
        with patch("random.choice", forced_tag_choice(get_tag("coupon"))):
            tags.award_random_tag(state, max_slots=5)
        self.assertTrue(state["free_shop_tag"])

    def test_d6_tag_sets_flag(self):
        state = make_state()
        with patch("random.choice", forced_tag_choice(get_tag("d6"))):
            tags.award_random_tag(state, max_slots=5)
        self.assertTrue(state["cheap_reroll_tag"])

    def test_voucher_tag_sets_flag(self):
        state = make_state()
        with patch("random.choice", forced_tag_choice(get_tag("voucher"))):
            tags.award_random_tag(state, max_slots=5)
        self.assertTrue(state["extra_voucher_tag"])

    def test_buffoon_tag_opens_pack_and_adds_jokers(self):
        state = make_state()
        with patch("random.choice", forced_tag_choice(get_tag("buffoon"))), \
             patch("builtins.input", return_value="1 2"):
            tags.award_random_tag(state, max_slots=5)
        self.assertEqual(len(state["jokers"]), 2)


# ---------------------------------------------------------------------------
# input_validation.py
# ---------------------------------------------------------------------------

class TestValidateInput(unittest.TestCase):

    def test_valid_selection_passthrough(self):
        self.assertEqual(iv.validate_input(["1", "3", "5"]), [0, 2, 4])

    def test_invalid_then_valid_retries(self):
        with patch("builtins.input", return_value="1 2"):
            result = iv.validate_input(["9", "9"])  # out of range 1-8, triggers retry
        self.assertEqual(result, [0, 1])


class TestValidatePlay(unittest.TestCase):

    def test_valid_play_passthrough(self):
        result = iv.validate_play("1", "Small Blind", hands=4, discards=3, max_hands=4, max_discards=3)
        self.assertEqual(result, [1])

    def test_skip_allowed_at_round_start(self):
        result = iv.validate_play("3", "Small Blind", hands=4, discards=3, max_hands=4, max_discards=3)
        self.assertEqual(result, [3])

    def test_skip_refused_on_boss_blind_then_retries(self):
        with patch("builtins.input", return_value="1"):
            result = iv.validate_play("3", "Boss Blind", hands=4, discards=3, max_hands=4, max_discards=3)
        self.assertEqual(result, [1])

    def test_skip_refused_mid_round_then_retries(self):
        with patch("builtins.input", return_value="1"):
            result = iv.validate_play("3", "Small Blind", hands=2, discards=3, max_hands=4, max_discards=3)
        self.assertEqual(result, [1])


class TestValidateEndless(unittest.TestCase):

    def test_accepts_uppercase(self):
        self.assertEqual(iv.validate_endless("Y"), "Y")
        self.assertEqual(iv.validate_endless("N"), "N")

    def test_accepts_lowercase_and_whitespace(self):
        self.assertEqual(iv.validate_endless(" y "), "Y")

    def test_invalid_then_valid_retries(self):
        with patch("builtins.input", return_value="Y"):
            result = iv.validate_endless("maybe")
        self.assertEqual(result, "Y")


class TestValidateShopChoice(unittest.TestCase):

    def test_leave(self):
        self.assertEqual(iv.validate_shop_choice("0", 5), "leave")

    def test_reroll(self):
        self.assertEqual(iv.validate_shop_choice("r", 5), "reroll")

    def test_destroy(self):
        self.assertEqual(iv.validate_shop_choice("d", 5), "destroy")

    def test_sell(self):
        self.assertEqual(iv.validate_shop_choice("s", 5), "sell")

    def test_valid_number(self):
        self.assertEqual(iv.validate_shop_choice("3", 5), 3)

    def test_out_of_range_then_valid(self):
        with patch("builtins.input", return_value="2"):
            result = iv.validate_shop_choice("9", 5)
        self.assertEqual(result, 2)


class TestValidateSellChoice(unittest.TestCase):

    def test_cancel(self):
        self.assertEqual(iv.validate_sell_choice("0", 3), "cancel")

    def test_valid_returns_zero_based_index(self):
        self.assertEqual(iv.validate_sell_choice("2", 3), 1)


class TestValidatePackPicks(unittest.TestCase):

    def test_valid_picks(self):
        self.assertEqual(iv.validate_pack_picks("1 3", 5, 2), [0, 2])

    def test_wrong_count_then_valid(self):
        with patch("builtins.input", return_value="1 2"):
            result = iv.validate_pack_picks("1", 5, 2)
        self.assertEqual(result, [0, 1])

    def test_duplicate_values_then_valid(self):
        with patch("builtins.input", return_value="1 2"):
            result = iv.validate_pack_picks("1 1", 5, 2)
        self.assertEqual(result, [0, 1])


class TestValidateDestroyInput(unittest.TestCase):

    def test_cancel(self):
        self.assertEqual(iv.validate_destroy_input("0"), "cancel")

    def test_valid_rank_suit(self):
        self.assertEqual(iv.validate_destroy_input("9 ♦"), ("9", "♦"))

    def test_case_insensitive_rank(self):
        self.assertEqual(iv.validate_destroy_input("k ♠"), ("K", "♠"))

    def test_invalid_then_valid_retries(self):
        with patch("builtins.input", return_value="9 ♦"):
            result = iv.validate_destroy_input("Z ♦")
        self.assertEqual(result, ("9", "♦"))


# ---------------------------------------------------------------------------
# main.py - round_setup / new_round_deck
# ---------------------------------------------------------------------------

class TestRoundSetup(unittest.TestCase):

    def test_base_values_with_no_bonuses(self):
        state = make_state()
        max_hands, max_discards, hand_size = main.round_setup(state)
        self.assertEqual((max_hands, max_discards, hand_size), (4, 3, 8))

    def test_permanent_bonuses_apply(self):
        state = make_state(bonus_hands=1, bonus_discards=2, bonus_hand_size=3)
        max_hands, max_discards, hand_size = main.round_setup(state)
        self.assertEqual((max_hands, max_discards, hand_size), (5, 5, 11))

    def test_joker_bonuses_apply(self):
        state = make_state(jokers=[
            {"type": "extra_hands", "value": 1},
            {"type": "hand_size", "value": 2},
        ])
        max_hands, max_discards, hand_size = main.round_setup(state)
        self.assertEqual((max_hands, max_discards, hand_size), (5, 3, 10))


class TestNewRoundDeck(unittest.TestCase):

    def test_deals_requested_hand_size(self):
        master = Deck().cards
        state = make_state(master_cards=master)
        deck, cards, remaining = main.new_round_deck(state, 8)
        self.assertEqual(len(cards), 8)
        self.assertEqual(remaining, 44)
        self.assertEqual(len(deck.cards), 44)

    def test_master_cards_untouched(self):
        master = Deck().cards
        state = make_state(master_cards=master)
        main.new_round_deck(state, 8)
        self.assertEqual(len(state["master_cards"]), 52)  # the original list is unmodified

    def test_smaller_master_deck_caps_deal(self):
        master = Deck().cards[:5]
        state = make_state(master_cards=master)
        deck, cards, remaining = main.new_round_deck(state, 8)
        self.assertEqual(len(cards), 5)
        self.assertEqual(remaining, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)