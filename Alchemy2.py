import re
import msvcrt

UNKNOWN = "?"

f_items = "items.txt"

recipes = {}

def getItems():
    retVal = []
    for recipe in recipes:
        retVal.append(recipe[0])
    retVal = list(set(retVal))
    retVal.sort()
    return retVal

def addItem(item = None):
    if item == None:
        data = input("What is the name of the new item: ")
        print(data)
        if data in getItems():
            print("That item already exists")
        else:
            pass

def removeItem():
    data = input("What item should be removed: ")

def addRecipe():
    a = input("First item: ")
    if a not in getItems():
        print("That item does not exist!")
        return

    b = input("Second item: ")
    if b not in getItems():
        print("That item does not exist!")
        return

def listItems():
    print()
    print(getItems())

def listKnownRecipes():
    print()
    for recipe in recipes:
        if recipes[recipe] != UNKNOWN:
            print("{} + {} = {}".format(recipe[0], recipe[1], recipes[recipe]))

def listUnknownRecipes():
    print()
    for recipe in recipes:
        if recipes[recipe] == UNKNOWN:
            print("{} + {} = {}".format(recipe[0], recipe[1], recipes[recipe]))

def menu():
    print()
    print("What would you like to do:")
    print("\ta: Add an item")
    print("\tr: Remove an item")
    print("\tc: Add a recipe")
    print("\ti: List items")
    print("\tl: List known recipes")
    print("\tu: List unknown recipes")
    print("\tq: Quit")

    data = msvcrt.getch().decode("utf-8")
    if data == "a": addItem()
    if data == "r": removeItem()
    if data == "c": addRecipe()
    if data == "i": listItems()
    if data == "u": listUnknownRecipes()
    if data == "l": listKnownRecipes()
    if data == "q": return -1

    return 0

with open(f_items, "r+") as f:
    lines = f.read().splitlines()

    # First we need to iterate through and find every possible item available
    itemList = []
    for line in lines:
        a = re.split('\+|=', line)
        for n in range(len(a)): a[n] = a[n].strip()    # [TODO] Find a more elegant way of doing this...

        # Here we merge lists to account for all possible items
        itemList += a

        # Here we account for existing recipes
        if len(a) == 3: recipes[(a[0], a[1])] = a[2]

    itemList = list(set(itemList))
    itemList.sort()

    # Then we create all possible connections between items
    for a in range(len(itemList)):
        for b in range(a, len(itemList)):
            c = itemList[a]
            d = itemList[b]
            # Ensure we don't overwrite a recipe if it already exists
            if (c, d) not in recipes:
                recipes[(c, d)] = UNKNOWN

    while True:
        ret = menu()
        if ret == -1: break

    print("\nThanks! Saving file...")

    #f.seek(0)
    #f.truncate(0)

    # [TODO] Write and call the save recipes stuff here
