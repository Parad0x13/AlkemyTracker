import re
import msvcrt

UNKNOWN = "?"

class Alchemy:
    def __init__(self):
        self.recipes = {}
        self.recipes = {("air", "earth"): "dust"}

        filename = "savefile.txt"

        f = open(filename, "r+")
        lines = f.read().splitlines()

        # First we need to iterate through and find every possible item/recipe available
        itemsFound = []
        recipesFound = {}
        for line in lines:
            a = re.split('\+|=', line)
            for n in range(len(a)): a[n] = a[n].strip()    # [TODO] Find a more elegant way of doing this...

            # Here we merge lists to account for all possible items
            itemsFound += a

            # Here we account for existing recipes
            if len(a) == 3: recipesFound[(a[0], a[1])] = a[2]

            # Here we error check for any erronous data in the savefile
            assert len(a) == 1 or len(a) == 3, "Incorrect data presented for line {}".format(line)

        for item in itemsFound: self.addItem(item)
        for recipe in recipesFound: self.addRecipe(recipe, recipesFound[recipe])

    def getItems(self):
        retVal = []

        # {(a, b): c} or {inputs: output}
        for recipe in self.recipes:
            retVal.append(recipe[0])
            retVal.append(recipe[1])
            retVal.append(self.recipes[recipe])

        retVal = list(set(retVal))
        try: retVal.remove(UNKNOWN)
        except: pass
        retVal.sort()
        return retVal

    def addItem(self, newItem = None):
        items = self.getItems()

        # Process user input
        if newItem == None:
            newItem = input("Name of item: ")
            if newItem in items:
                print("That item already exists")
                return
            self.addItem(newItem)

        # Here we create a recipe for our item against all other items that exist
        self.addRecipe((newItem, newItem), UNKNOWN)
        for item in items:
            if item == UNKNOWN: continue
            # Here we just sort the two input values by alpha so they are standardized... for now!
            # This is a VERY VERY VERY dumb way of doing this...
            # [TODO] Fix this nonsense
            a = item
            b = newItem
            c = UNKNOWN

            if b < a:
                a = newItem
                b = item

            self.addRecipe((a, b), c)

        return

    def removeItem(self, oldItem = None):
        items = self.getItems()

        # Process user input
        if oldItem == None:
            oldItem = input("Name of item: ")
            if oldItem not in items:
                print("That item does not exist")
                return
            self.removeItem(oldItem)

        oldRecipes = []
        for recipe in self.recipes:
            if recipe[0] == oldItem: oldRecipes.append(recipe)
            elif recipe[1] == oldItem: oldRecipes.append(recipe)
            elif self.recipes[recipe] == oldItem: oldRecipes.append(recipe)

        for oldRecipe in oldRecipes: self.removeRecipe(oldRecipe)
        print(self.recipes)

    def renderItems(self):
        items = self.getItems()
        for item in items: print(item)

    def addRecipe(self, inputs = None, output = None):
        if UNKNOWN in inputs: return

        # Process user input
        if inputs == None and output == None:
            pass

        # This will automatically overwrite any lingering recipe that resolves into UNKNOWN
        self.recipes[inputs] = output

    def removeRecipe(self, recipe = None):
        # Process user input
        if recipe == None:
            a = input("Item A: ")
            b = input("Item B: ")

            # [TODO] Fix this and do it the right way. No need to have both a, b AND b, a
            recipe = (a, b)
            self.removeRecipe(recipe)
            recipe = (b, a)
            self.removeRecipe(recipe)

        if recipe in self.recipes:
            a = recipe[0]
            b = recipe[1]
            c = self.recipes[recipe]
            del self.recipes[recipe]

    def renderRecipes(self, known):
        print()
        for recipe in sorted(self.recipes):
            if known and self.recipes[recipe] != UNKNOWN:
                print("{} + {} = {}".format(recipe[0], recipe[1], self.recipes[recipe]))
            elif not known and self.recipes[recipe] == UNKNOWN:
                print("{} + {} = {}".format(recipe[0], recipe[1], self.recipes[recipe]))

    def menu(self):
        print()
        print("What would you like to do:")
        print("\ta: Add an item")
        print("\tr: Remove an item")
        print("\tc: Clear a recipe")
        print("\ti: List items")
        print("\tk: List known recipes")
        print("\tu: List unknown recipes")
        print("\tq: Quit")

        data = msvcrt.getch().decode("utf-8")
        if data == "a": self.addItem()
        if data == "r": self.removeItem()
        if data == "c": self.removeRecipe()
        if data == "i": self.renderItems()
        if data == "k": self.renderRecipes(known = True)
        if data == "u": self.renderRecipes(known = False)
        if data == "q": return -1

        return 0

    def run(self):
        while True:
            ret = self.menu()
            if ret == -1: break

        print("\nSaving File...")

alchemy = Alchemy()
alchemy.run()
