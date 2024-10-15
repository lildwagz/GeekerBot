import random


def slot():
    fruits = ':green_apple:,:apple:,:pear:,:tangerine:,:lemon:,:banana:,:watermelon:,:grapes:,:strawberry:,:melon:,' \
             ':cherries:,:peach:,:mango:,:pineapple:,:tomato:,:eggplant:,:flushed:'.split(',')
    return [random.choice(fruits), random.choice(fruits), random.choice(fruits)]

def slotify(slot):
    return ' | '.join(slot)