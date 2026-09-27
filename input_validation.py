from card import RANKS, SUITS


def validate_input(selected_cards):
    while True:

        if len(selected_cards) == 0 or len(selected_cards) > 5:
            print()
            print("Please input atleast 1 and upto 5 maximum values")

        elif not all(i.isdigit() for i in selected_cards):
            print()
            print("Please input numbers only")

        elif any(int(i) < 1 or int(i) > 8 for i in selected_cards):
            print()
            print("Please input values between 1-8")

        elif len(selected_cards) != len(set(selected_cards)):
            print()
            print("Please input unique values")

        else:
            return [int(number) - 1 for number in selected_cards]

        print()
        selected_cards = input("Select up to 5 cards by entering their numbers separated by spaces: ").split()

def validate_play(play, blind, hands, discards, max_hands, max_discards):
    play = play.strip()
    while True:

        if len(play) != 1:
            print()
            print("Please input 1 integer value between 1 and 3 only!")

        elif not all(i.isdigit() for i in play):
            print()
            print("Please input integer only!")

        elif int(play) < 1 or int(play) > 3:
            print()
            print("Please input a value between 1 and 3 only!")

        elif int(play) == 3 and blind == "Boss Blind":
            print()
            print("You cannot skip a Boss Blind!")

        elif int(play) == 3 and (hands != max_hands or discards != max_discards):
            print()
            print("You cannot skip a Blind after choosing to play it!")

        else:
            return [int(play[0])]

        print()
        play = input("Choice: ")


def validate_endless(choice):
    while True:
        choice = choice.strip().upper()

        if choice == "Y" or choice == "N":
            return choice

        print()
        print("Please enter Y or N only!")
        choice = input("Choice: ")


def validate_shop_choice(choice, num_options):
    while True:
        choice = choice.strip().upper()

        if choice == "0":
            return "leave"

        elif choice == "R":
            return "reroll"

        elif choice == "D":
            return "destroy"

        elif choice == "S":
            return "sell"

        elif choice.isdigit() and 1 <= int(choice) <= num_options:
            return int(choice)

        else:
            print()
            print(f"Please enter a number between 1-{num_options}, R to reroll, D to destroy, S to sell a Joker, or 0 to leave.")

        choice = input("Choice: ")


def validate_sell_choice(raw, num_jokers):
    while True:
        raw = raw.strip()

        if raw == "0":
            return "cancel"

        elif raw.isdigit() and 1 <= int(raw) <= num_jokers:
            return int(raw) - 1

        else:
            print()
            print(f"Please enter a number between 1-{num_jokers}, or 0 to cancel.")

        raw = input("Joker number to sell, or 0 to cancel: ")


def validate_pack_picks(raw, num_options, pick_count):
    while True:
        tokens = raw.split()

        if len(tokens) != pick_count:
            print()
            print(f"Please enter exactly {pick_count} number(s).")

        elif not all(t.isdigit() for t in tokens):
            print()
            print("Please input numbers only.")

        elif any(int(t) < 1 or int(t) > num_options for t in tokens):
            print()
            print(f"Please input values between 1-{num_options}.")

        elif len(set(tokens)) != len(tokens):
            print()
            print("Please input unique values.")

        else:
            return [int(t) - 1 for t in tokens]

        raw = input(f"Pick {pick_count} card number(s) separated by spaces: ")


def validate_destroy_input(raw):
    valid_ranks = [r.upper() for r in RANKS]

    while True:
        raw = raw.strip()

        if raw == "0":
            return "cancel"

        tokens = raw.split()

        if len(tokens) != 2 or tokens[0].upper() not in valid_ranks or tokens[1] not in SUITS:
            print()
            print("Please enter a rank and suit (e.g. '9 ♦'), or 0 to cancel.")

        else:
            rank = RANKS[valid_ranks.index(tokens[0].upper())]
            suit = tokens[1]
            return (rank, suit)

        raw = input("Card to destroy (rank suit), or 0 to cancel: ")