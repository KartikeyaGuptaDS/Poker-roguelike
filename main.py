from card import Card, Deck
from poker import evaluate_hand
from scoring import calc_score, target_score
from input_validation import validate_input, validate_play, validate_endless
from shop import run_shop, get_joker_bonus, JOKER_SLOTS
import tags
from display import (
major_separator,
show_welcome,
show_ante,
show_round_info,
show_boss_effect,
show_hand,
show_deck_count,
show_action_menu,
show_played_cards,
show_result,
show_new_cards,
show_discarded_cards,
show_money
)

BASE_HANDS = 4
BASE_DISCARDS = 3
BASE_HAND_SIZE = 8
BASE_INTEREST_CAP = 5


def round_setup(state):

    max_hands = BASE_HANDS + state["bonus_hands"] + get_joker_bonus(state["jokers"], "extra_hands")
    max_discards = BASE_DISCARDS + state["bonus_discards"] + get_joker_bonus(state["jokers"], "extra_discards")
    hand_size = BASE_HAND_SIZE + state["bonus_hand_size"] + get_joker_bonus(state["jokers"], "hand_size")
    return max_hands, max_discards, hand_size


def new_round_deck(state, hand_size):

    deck = Deck()
    deck.cards = list(state["master_cards"])
    deck.shuffle()
    cards, remaining_cards = deck.deal_card(hand_size)
    return deck, cards, remaining_cards


def main():
    show_welcome()

    difficulty = input("Enter the difficulty level: ").strip().title()

    ante = 1
    total_score = 0
    blind = "Small Blind"
    skip_tags = 0
    endless = False

    starter_deck = Deck()

    state = {
        "money": 0,
        "jokers": [],
        "vouchers": [],
        "hand_levels": {},
        "master_cards": starter_deck.cards,
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

    max_hands, max_discards, hand_size = round_setup(state)
    hands = max_hands
    discards = max_discards

    deck, cards, remaining_cards = new_round_deck(state, hand_size)

    while ante <= 8 or endless == True:

        show_ante(ante, blind)

        if blind == "Boss Blind" and state.get("boss_effect") is None:
            state["boss_effect"] = tags.pick_boss_effect()
        if blind == "Boss Blind":
            show_boss_effect(state["boss_effect"])

        boss_mult = (state.get("boss_effect") or {}).get("target_mult", 2)
        target = target_score(ante, difficulty, blind, boss_mult=boss_mult)

        show_round_info(total_score, target, hands, discards)

        show_hand(cards)
        show_deck_count(remaining_cards)

        if discards > 0:
            show_action_menu(blind, hands, discards, max_hands, max_discards)

            play = input("Choice: ")
            play = validate_play(play, blind, hands, discards, max_hands, max_discards)
            print()
            play = int(play[0])

        else:
            play = 1

        if play == 1:

            selected_cards = input("Select up to 5 cards by entering their numbers separated by spaces: ").split()

            selected_cards = validate_input(selected_cards)

            selected_cards = [cards[i] for i in selected_cards]

            show_played_cards(selected_cards)

            # Evaluate and score the cards that were played
            result = evaluate_hand(selected_cards)

            score = calc_score(selected_cards, result, state["jokers"], state["hand_levels"],
                                discards, remaining_cards, state["money"])

            total_score += score

            state["money"] += get_joker_bonus(state["jokers"], "money_hand")

            show_result(result, score, total_score, target)

            # Remove played cards from the player's hand
            for card in selected_cards:
                cards.remove(card)

            # Deal the same number of cards that were played
            new_cards, remaining_cards = deck.deal_card(len(selected_cards))

            cards.extend(new_cards)

            show_new_cards(new_cards, cards, remaining_cards)

            hands -= 1

        elif play == 2:

            discards -= 1

            selected_cards = input("Select up to 5 cards by entering their numbers separated by spaces: ").split()

            selected_cards = validate_input(selected_cards)

            selected_cards = [cards[i] for i in selected_cards]

            show_discarded_cards(selected_cards)

            state["money"] += get_joker_bonus(state["jokers"], "money_discard")

            for card in selected_cards:
                cards.remove(card)

            new_cards, remaining_cards = deck.deal_card(len(selected_cards))

            cards.extend(new_cards)

            show_new_cards(new_cards, cards, remaining_cards)

        elif play == 3:

            skip_tags += 1

            print("Blind Skipped!")

            max_slots_now = JOKER_SLOTS + state["bonus_joker_slots"]
            tag_result = tags.award_random_tag(state, max_slots_now)

            if tag_result["juggle_gain"]:
                extra_cards, remaining_cards = deck.deal_card(tag_result["juggle_gain"])
                cards.extend(extra_cards)
                print(f"Your hand size is temporarily +{len(extra_cards)} for this round!")

            if blind == "Small Blind":
                blind = "Big Blind"
            elif blind == "Big Blind":
                blind = "Boss Blind"

        """if total_score < target and play != 3:
            print()"""

        # Check whether the target has been reached
        if total_score >= target:

            interest_cap = BASE_INTEREST_CAP + state["bonus_interest_cap"] + get_joker_bonus(state["jokers"], "interest_cap")
            interest = min(state["money"] // 5, interest_cap)

            hand_money = hands
            state["money"] += hands + interest

            just_beat_boss = False

            if blind == "Small Blind":

                blind_money = 3
                state["money"] += blind_money

                show_money(blind, hand_money, interest, blind_money, state["money"])

                blind = "Big Blind"

            elif blind == "Big Blind":

                blind_money = 4
                state["money"] += blind_money

                show_money(blind, hand_money, interest, blind_money, state["money"])

                blind = "Boss Blind"

            elif blind == "Boss Blind":

                blind_money = 5
                state["money"] += blind_money

                show_money(blind, hand_money, interest, blind_money, state["money"])

                if state.get("investment_bonus"):
                    bonus = state["investment_bonus"]
                    state["money"] += bonus
                    print(f"Investment Tag paid out: +${bonus}!")
                    state["investment_bonus"] = 0

                blind = "Small Blind"
                just_beat_boss = True
                state["boss_effect"] = None

                major_separator()
                print(f"                    ANTE {ante} COMPLETE!")
                major_separator()
                major_separator()
                ante += 1

                if ante == 9:
                    print("YOU WON!")
                    print("You have successfully completed all Ante(s)!")
                    print("Do you want to continue into endless?")
                    print("Type Y for yes and N for no.")
                    a = input("Enter Choice: ")
                    a = validate_endless(a)

                    if a == "Y":
                        endless = True
                    elif a == "N":
                        endless = False
                        print()
                        print("Thanks for playing!")
                        break

            # Visit the shop after every blind; the Voucher slot only appears
            # right after a Boss Blind.
            state = run_shop(state, after_boss=just_beat_boss)

            total_score = 0
            max_hands, max_discards, hand_size = round_setup(state)
            hands = max_hands
            discards = max_discards

            major_separator()
            print()
            print("Preparing next round...")

            deck, cards, remaining_cards = new_round_deck(state, hand_size)

        elif hands == 0:

            print()
            major_separator()
            print("                         GAME OVER")
            major_separator()

            print()
            print("You did not reach the target score for this round.")
            print()

            break

    major_separator()


if __name__ == "__main__":
    main()