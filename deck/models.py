import random
import string
import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser


def random_string():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12))


class User(AbstractUser):
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['date_joined', ]

    def __unicode__(self):
        return self.email


MINOR_VALUES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'P', 'N', 'Q', 'K']
MAJOR_ARCANA_VALUES = {
    '0': 'THE FOOL',
    '1': 'THE MAGICIAN',
    '2': 'THE HIGH PRIESTESS',
    '3': 'THE EMPRESS',
    '4': 'THE EMPEROR',
    '5': 'THE HIEROPHANT',
    '6': 'THE LOVERS',
    '7': 'THE CHARIOT',
    '8': 'STRENGTH',
    '9': 'THE HERMIT',
    'A': 'WHEEL OF FORTUNE',
    'B': 'JUSTICE',
    'C': 'THE HANGED MAN',
    'D': 'DEATH',
    'E': 'TEMPERANCE',
    'F': 'THE DEVIL',
    'G': 'THE TOWER',
    'H': 'THE STAR',
    'I': 'THE MOON',
    'J': 'THE SUN',
    'K': 'JUDGEMENT',
    'L': 'THE WORLD'
}

CARDS = [v + s for s in ['W', 'C', 'S', 'P'] for v in MINOR_VALUES] + [k + 'M' for k in MAJOR_ARCANA_VALUES.keys()]
JOKERS = []

SUITS = {
    'W': 'WANDS',
    'C': 'CUPS',
    'S': 'SWORDS',
    'P': 'PENTACLES',
    'M': 'MAJOR'
}
VALUES = {
    'A': 'ACE',
    '2': '2',
    '3': '3',
    '4': '4',
    '5': '5',
    '6': '6',
    '7': '7',
    '8': '8',
    '9': '9',
    '0': '10',
    'P': 'PAGE',
    'N': 'KNIGHT',
    'Q': 'QUEEN',
    'K': 'KING'
}

class Deck(models.Model):
    key = models.CharField(default=random_string, max_length=15, db_index=True)
    last_used = models.DateTimeField(default=datetime.datetime.now)
    deck_count = models.IntegerField(default=1)
    stack = models.JSONField(null=True, blank=True) #The cards that haven't been drawn yet.
    piles = models.JSONField(null=True, blank=True) 
    deck_contents = models.JSONField(null=True, blank=True) #All the cards that should be included when shuffling and whatnot
    shuffled = models.BooleanField(default=False)
    include_jokers = models.BooleanField(default=False)
    
    def open_new(self, cards_used=None, jokers_enabled=False):
        self.include_jokers = False if jokers_enabled is None else jokers_enabled
        stack = []
        if cards_used is None: # use all the cards
            if self.deck_contents is None:
                cards = (CARDS, CARDS + JOKERS)[self.include_jokers]
            else:
                cards = self.deck_contents[:]
        else: # use a subset of a standard deck
            cards_used = cards_used.upper()
            # Only allow real cards
            valid_cards = (CARDS, CARDS + JOKERS)[self.include_jokers]
            cards = [x for x in cards_used.split(",") if x in valid_cards]
            self.deck_contents = cards[:]  # save the subset for future shuffles

        for i in range(0, self.deck_count):  # for loop over how many decks someone wants. Blackjack is usually 6.
            stack = stack + cards[:]  # adding the [:] forces the array to be copied.
        self.stack = stack
        self.last_used = datetime.datetime.now()
        self.save()

    def save(self, *args, **kwargs):
        self.last_used = datetime.datetime.now()
        super(Deck, self).save(*args, **kwargs)

def card_to_dict(card):
    value = card[:1]
    suit = card[1:]

    code = value + suit
    card_dict = {
        'code': code,
        'image': 'https://deckofcardsapi.com/static/img/%s.png' % code,
        'images': {
            'svg': 'https://deckofcardsapi.com/static/img/%s.svg' % code,
            'png': 'https://deckofcardsapi.com/static/img/%s.png' % code
        }
    }

    if suit == 'M':
        card_dict['value'] = MAJOR_ARCANA_VALUES.get(value, value)
        card_dict['suit'] = SUITS.get(suit, suit)
    else:
        card_dict['value'] = VALUES.get(value) or value
        card_dict['suit'] = SUITS.get(suit) or suit
    return card_dict
