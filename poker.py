from collections import Counter

from card import Card

def evaluate_hand(hand):

    rank_counts = Counter(card.rank for card in hand)
    counts = list(rank_counts.values())
    suits = [card.suit for card in hand]
    max_count = max(counts)

    # Special 5-card combinations
    if len(hand) == 5:

        # Check for Flush
        is_flush = len(set(suits)) == 1

        # Check for Straight
        sorted_values = sorted(card.value for card in hand)

        is_straight = (len(set(sorted_values)) == 5 and sorted_values[-1] - sorted_values[0] == 4)

        # Ace-low straight: A, 2, 3, 4, 5
        if sorted_values == [2, 3, 4, 5, 14]:
                is_straight = True

        # Full House
        is_full_house = max_count == 3 and 2 in counts

        # Five of a Kind
        is_five_of_a_kind = max_count == 5

        # Flush Five
        is_flush_five = (len(set(card.rank for card in hand)) == 1 and len(set(card.suit for card in hand)) == 1)

        # Flush Five
        if is_flush_five:
            return "Flush Five"

        # Flush House
        if is_flush and is_full_house:
            return "Flush House"

        # Five of a Kind
        elif is_five_of_a_kind:
            return "Five of a Kind"

        # Straight Flush
        if is_straight and is_flush:
            return "Straight Flush"
        # Flush
        elif is_flush:
            return "Flush"

        # Straight
        elif is_straight:
            return "Straight"

        # Full House
        elif is_full_house:
            return "Full House"

    # Duplicate-based combinations
    if max_count == 4:
        return "Four of a Kind"

    elif max_count == 3:
        return "Three of a Kind"

    elif max_count == 2:
        if counts.count(2) == 2:
            return "Two Pair"
        else:
            return "One Pair"

    else:
        return "High Card"