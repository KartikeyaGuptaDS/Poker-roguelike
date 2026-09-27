import random

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
SUITS = ["♠", "♥", "♦", "♣"]
RANK_VALUES = {rank: i + 2 for i, rank in enumerate(RANKS)}


class Card:
    def __init__(self, rank, suit, value, enhancement=None, bonus_chips=0, bonus_mult=0):
        self.rank = rank
        self.suit = suit
        self.value = value

        # enhancement is None, "bonus" (+chips when played) or "mult" (+mult when played).
        # These come from Standard Packs bought in the shop.
        self.enhancement = enhancement
        self.bonus_chips = bonus_chips
        self.bonus_mult = bonus_mult

    def show_card(self):
        label = f"{self.rank}{self.suit}"
        if self.enhancement == "bonus":
            label += "c"
        elif self.enhancement == "mult":
            label += "m"
        return label

    def get_value(self):
        return self.value + self.bonus_chips

    def describe(self):
        base = f"{self.rank}{self.suit}"
        if self.enhancement == "bonus":
            return f"{base}  (Bonus Card: +{self.bonus_chips} Chips)"
        elif self.enhancement == "mult":
            return f"{base}  (Mult Card: +{self.bonus_mult} Mult)"
        return base


class Deck:
    def __init__(self):
        self.cards = []
        self.build_deck()

    def build_deck(self):
        for suit in SUITS:
            for rank in RANKS:
                self.cards.append(Card(rank, suit, RANK_VALUES[rank]))

    def show_deck(self):
        return [card.show_card() for card in self.cards]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self, n=1):
        dealt_cards = []

        for i in range(min(n, len(self.cards))):
            card = self.cards.pop()
            dealt_cards.append(card)

        return dealt_cards, len(self.cards)

    def choose_card(self, rank, suit):
        for card in self.cards:
            if card.rank == rank and card.suit == suit:
                self.cards.remove(card)
                return card
        return None