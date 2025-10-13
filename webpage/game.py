import random

SUITS = {'H': 'red', 'D': 'red', 'C': 'black', 'S': 'black'}
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

class Card:
    def __init__(self, suit, rank, is_face_up=False):
        self.suit = suit
        self.rank = rank
        self.is_face_up = is_face_up

    @property
    def color(self):
        return SUITS[self.suit]

    def __repr__(self):
        return f"{self.rank}{self.suit}"

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

def create_deck():
    return [Card(suit, rank) for suit in SUITS for rank in RANKS]

class Game:
    def __init__(self):
        self.deck = shuffle_deck(create_deck())
        self.tableau = [[] for _ in range(7)]
        self.foundations = [[] for _ in range(4)]
        self.stock = []
        self.talon = []
        self.deal()

    def deal(self):
        for i in range(7):
            for j in range(i, 7):
                card = self.deck.pop()
                if i == j:
                    card.is_face_up = True
                self.tableau[j].append(card)
        self.stock = self.deck
        self.deck = []

    def draw_from_stock(self):
        if not self.stock:
            self.stock = self.talon[::-1]
            for card in self.stock:
                card.is_face_up = False
            self.talon = []
        elif self.stock:
            card = self.stock.pop()
            card.is_face_up = True
            self.talon.append(card)

    def can_move_to_tableau(self, card, pile):
        if not pile:
            return card.rank == 'K'
        top_card = pile[-1]
        return card.color != top_card.color and RANKS.index(card.rank) == RANKS.index(top_card.rank) - 1

    def can_move_to_foundation(self, card, pile):
        if not pile:
            return card.rank == 'A'
        top_card = pile[-1]
        return card.suit == top_card.suit and RANKS.index(card.rank) == RANKS.index(top_card.rank) + 1

    def move_card(self, from_pile, to_pile, card):
        if card in from_pile:
            # When moving a stack of cards from the tableau
            if isinstance(from_pile, list) and from_pile in self.tableau:
                card_index = from_pile.index(card)
                cards_to_move = from_pile[card_index:]
                if self.can_move_to_tableau(card, to_pile):
                    del from_pile[card_index:]
                    to_pile.extend(cards_to_move)
                    if from_pile and not from_pile[-1].is_face_up:
                        from_pile[-1].is_face_up = True
                    return True
            # When moving a single card
            elif self.can_move_to_tableau(card, to_pile) or self.can_move_to_foundation(card, to_pile):
                from_pile.remove(card)
                to_pile.append(card)
                if from_pile and from_pile in self.tableau and not from_pile[-1].is_face_up:
                    from_pile[-1].is_face_up = True
                return True
        return False

    def is_won(self):
        return all(len(f) == 13 for f in self.foundations)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

def shuffle_deck(deck):
    random.shuffle(deck)
    return deck
