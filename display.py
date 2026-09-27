def separator():
    print("-" * 60)

def major_separator():
    print("=" * 60)

def show_welcome():
    major_separator()
    print("                   WELCOME TO ANTE UP!")
    major_separator()

    print()
    print("A solo, roguelike poker game. Across 8 Antes, you'll face ")
    print("three Blinds each (Small, Big, Boss), building a poker")
    print("hand up to a target score before your hands run out.")
    print()

    print("HOW A ROUND WORKS")
    separator()
    print("- You're dealt a hand of cards (8 to start, more with upgrades).")
    print("- Each turn, either:")
    print("    1. Play a hand: pick 1-5 cards. They're scored as the best")
    print("       poker hand they form (High Card up to Flush Five), then")
    print("       replaced with new cards from the deck.")
    print("    2. Discard: swap up to 5 unwanted cards for new ones, without")
    print("       scoring - costs one of your limited discards.")
    print("- Reach the target score before you run out of hands to clear")
    print("  the Blind. Run out of hands first and it's Game Over.")
    print("- Small and Big Blinds can be skipped instead of played, which")
    print("  awards a random Tag (a bonus effect or reward) - but you get no")
    print("  money for skipping, and Boss Blinds can never be skipped.")
    print()

    print("SCORING")
    separator()
    print("- Each poker hand has a base Chips and Mult value. Chips add up")
    print("  from the base, your cards' own values, and any bonuses; the")
    print("  total is then multiplied by Mult: Score = Chips x Mult.")
    print("- Planet cards permanently level up a hand type's base Chips and")
    print("  Mult. Jokers add passive bonuses of their own every hand played.")
    print()

    print("THE SHOP")
    separator()
    print("- After every Blind you visit the shop to spend money on Jokers,")
    print("  Planet cards, Booster Packs, and (after a Boss Blind) Vouchers.")
    print("- You can also reroll the shop's stock, sell Jokers you own for")
    print("  cash, or destroy a card from your deck for good.")
    print("- Money carries over between rounds, and unspent money earns a")
    print("  little interest, so it's worth not spending every dollar.")
    print()

    print("DIFFICULTY")
    separator()
    print("- There are 3 Difficulty levels: White, Black, Gold")
    print("- Difficulty level affects the target score for each round.")
    print("- Please select the difficulty level from the options above.")
    print()


def show_ante(ante, blind):
    print()
    major_separator()
    print(f"                         ANTE {ante}")
    if blind == "Small Blind":
        print("                      Small Blind")
    elif blind == "Big Blind":
        print("                       Big Blind")
    elif blind == "Boss Blind":
        print("                       Boss Blind")
    major_separator()

def show_round_info(total_score, target, hands, discards):
    print()
    print(f"Score: {total_score} / {target}          Hands: {hands}          Discards: {discards}")
    print()

def show_boss_effect(boss_effect):
    if boss_effect:
        print(f"Boss Encounter: {boss_effect['name']} - {boss_effect['desc']}")
        print()

def show_hand(cards):
    print("YOUR HAND")
    separator()

    for i in range(0, len(cards), 4):
        row = ""
        for j in range(i, min(i + 4, len(cards))):
            row += f"{j + 1}. {cards[j].show_card():<5}"
        print(row)

    separator()

def show_deck_count(remaining_cards):
    print(f"Deck: {remaining_cards} cards")
    print()

def show_action_menu(blind, hands, discards, max_hands, max_discards):
    print("ACTION")
    separator()

    print("1. Play hand")
    print("2. Discard cards")

    if blind == "Small Blind" or blind == "Big Blind":
        if hands == max_hands and discards == max_discards:
            print("3. Skip blind")

    print()

def show_played_cards(selected_cards):
    print()
    print("PLAYED")
    separator()

    for card in selected_cards:
        print(card.show_card())
    print()

def show_result(result, score, total_score, target):
    print("RESULT")
    separator()

    print("Hand: ", result)
    print("Score: ", score)
    print(f"Round Score: {total_score} / {target}")

def show_new_cards(new_cards, cards, remaining_cards):
    print()
    print("NEW CARDS")
    separator()

    for card in new_cards:
        print(card.show_card())

    print()
    print(f"Cards remaining in hand: {len(cards)}")
    print(f"Deck: {remaining_cards} cards")

def show_discarded_cards(selected_cards):
    print()
    print("DISCARDED")
    separator()

    for card in selected_cards:
        print(card.show_card())

def show_money(blind, hand_money, interest, blind_money, total_money):
    print()
    major_separator()
    if blind == "Small Blind":
        print("                    SMALL BLIND COMPLETE")
    elif blind == "Big Blind":
        print("                     BIG BLIND COMPLETE")
    elif blind == "Boss Blind":
        print("                    BOSS BLIND COMPLETE!")
    major_separator()
    print("                        MONEY EARNED")
    print()
    if hand_money > 0:
        print("From Hands: ", "$" * hand_money)
    if interest > 0:
        print("Interest  : ", "$" * interest)
    print(f"From {blind}: ", "$" * blind_money)
    print()
    print(f"                       TOTAL MONEY: {total_money}$")
    major_separator()


# ---------------------------------------------------------------------------
# Shop displays
# ---------------------------------------------------------------------------

def show_owned_jokers(jokers):
    print()
    print("YOUR JOKERS")
    separator()
    if not jokers:
        print("(none yet)")
    for joker in jokers:
        print(f"- {joker['name']}: {joker['desc']}")


def show_shop(money, entries, max_slots, num_jokers, reroll_cost, destroy_cost):
    print()
    major_separator()
    print("                           SHOP")
    major_separator()
    print(f"  Money: ${money}                               Joker slots: {num_jokers}/{max_slots}")

    section_titles = {
        "card": "CARDS (Jokers & Planets)",
        "pack": "BOOSTER PACKS",
        "voucher": "VOUCHER",
    }

    current_section = None
    for entry in entries:
        if entry["section"] != current_section:
            current_section = entry["section"]
            print()
            print(section_titles[current_section])
            separator()
        print(f"{entry['number']}. {entry['label']:<32} ${entry['cost']}")
        print(f"   {entry['desc']}")
    if not entries:
        print("(shop is empty)")
    print()

    separator()
    print(f"R. Reroll shop (${reroll_cost})")
    print(f"D. Destroy a card (${destroy_cost})")
    print("S. Sell a Joker")
    print("0. Leave shop")
    print()


def show_pack_options(pack_name, labels, pick_count):
    print()
    print(f"OPENING: {pack_name}")
    separator()
    for i, label in enumerate(labels):
        print(f"{i + 1}. {label}")
    print()
    print(f"Choose {pick_count} card(s).")


def show_destroy_prompt():
    print()
    print("DESTROY A CARD")
    separator()
    print("This permanently removes a card from your deck - it will never be dealt again.")
    print("Enter the rank and suit of the card, e.g. '9 ♦' or 'K ♠'.")


def show_shop_message(message):
    print()
    print(message)