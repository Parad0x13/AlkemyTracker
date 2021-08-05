import re
import msvcrt

UNKNOWN = "?"
NOTHING = "nothing"
LEVEL_LOW = "+"
LEVEL_MED = "?"
LEVEL_HIGH = "!"

class Alchemy:
    def __init__(self):
        self.filename = "savefile.txt"
        self.recipes = {}
        self.load()

    def load(self):
        f = open(self.filename, "r+")
        lines = f.read().splitlines()
        f.close()

        # The very first thing we need to do is create a listing of every item and recipe mentioned in the savefile
        itemsFound = []
        recipesFound = {}
        for line in lines:
            a = re.split("\+|=", line)
            for n in range(len(a)): a[n] = a[n].strip()    # [TODO] Find a more elegant way of doing this...

            # Here we merge whatever items we found into all possible items
            itemsFound += a

            # Here we account for any recipes found
            if len(a) == 3: recipesFound[(a[0], a[1])] = a[2]

            # Here we error check for any erronous data in the savefile
            assert len(a) == 1 or len(a) == 3, "Incorrect data presented for line {}".format(line)

        # Ensure we have no duplicates
        itemsFound = list(set(itemsFound))
        itemsFound.sort()    # Not needed but I like it anyways

        # Now we add all our found items to our instance
        # This will create recipes for every possible item match
        for item in itemsFound: self.addItem(item)

        # Now we add all our found recipes to our instance
        for recipe in recipesFound: self.addRecipe(recipe, recipesFound[recipe])

    def save(self):
        print("\nSaving...")

        items = self.getItems()

        f = open(self.filename, "r+")

        # Erase the file
        f.seek(0)
        f.truncate(0)

        for item in items:
            f.write(item + "\n")

        for recipe in self.recipes:
            a = recipe[0]
            b = recipe[1]
            c = self.recipes[recipe]
            f.write("{} + {} = {}\n".format(a, b, c))

        f.close()

    # This is accomplished by iterating through every recipe and finding all possible items
    def getItems(self):
        items = []

        for recipe in self.recipes:
            items.append(recipe[0])
            items.append(recipe[1])
            items.append(self.recipes[recipe])

        items = list(set(items))

        if NOTHING in items: items.remove(NOTHING)
        if UNKNOWN in items: items.remove(UNKNOWN)

        items.sort()    # Not needed but I like it anyways

        return items

    def addItem(self, item = None):
        if item == NOTHING: return

        if item != None: self.log("Attempting to add item {}".format(item))

        # Process user input
        if item == None:
            self.log("Attempting to add a user specified item")

            item = input("Item name: ").strip()
            self.addItem(item)

            return

        items = self.getItems()

        if item in items:
            self.log("That item already exists", level = LEVEL_MED)
            return

        self.addRecipe((item, item), UNKNOWN)
        for _ in items: self.addRecipe((_, item), UNKNOWN)

    def removeItem(self, item = None):
        if item != None: self.log("Attempting to remove item {}".format(item))

        # Process user input
        if item == None:
            self.log("Attempting to remove a user specified item")

            item = input("Item name: ").strip()
            self.removeItem(item)

            return

        items = self.getItems()

        if item not in items:
            self.log("That item does not exist", level = LEVEL_MED)
            return

        recipes = self.getRecipesContainingItem(item)
        for recipe in recipes: self.removeRecipe(recipe)

    def renderItems(self):
        items = self.getItems()
        for item in items: print(item)
        print("\ndiscovered {} items".format(len(items)))

    def addRecipe(self, inputs = None, output = None):
        if inputs != None and output != None: self.log("Attempting to add recipe {} + {} = {}".format(inputs[0], inputs[1], output))

        # Process user input
        if inputs == None and output == None:
            self.log("Attempting to add a user specified recipe")

            a = input("Item A: ").strip()
            b = input("Item B: ").strip()
            c = input("Item result: ").strip()

            # Here we check if the user referenced any new items during the generation of this new recipe
            items = self.getItems()
            for item in [a, b, c]:
                if item not in items:
                    self.addItem(item)

            self.addRecipe((a, b), c)

            return

        assert inputs != None and output != None, "Error in addRecipe()"

        if UNKNOWN in inputs: return    # We don't want to process any recipes whose inputs are unknown
        if "" in inputs: return    # Likewise we don't want to process recipes that have no item names

        # Here we ensure alphanumerics are upheld in the recipe
        # [TODO] Find a more elegant way of doing this, I don't like this method at all
        a = inputs[0]
        b = inputs[1]
        if b < a:
            a = inputs[1]
            b = inputs[0]

        if (a, b) in self.recipes and self.recipes[(a, b)] != UNKNOWN:
            self.log("Recipe already exists", level = LEVEL_MED)
            return

        self.recipes[(a, b)] = output

    def removeRecipe(self, inputs = None):
        if inputs != None: self.log("Attempting to remove recipe {}".format(inputs))

        # Process user input
        if inputs == None:
            a = input("Item A: ").strip()
            b = input("Item B: ").strip()
            self.removeRecipe((a, b))
            return

        # Here we ensure alphanumerics are upheld in the recipe
        # [TODO] Find a more elegant way of doing this, I don't like this method at all
        a = inputs[0]
        b = inputs[1]
        if b < a:
            a = inputs[1]
            b = inputs[0]

        del self.recipes[(a, b)]

    def getRecipesContainingItem(self, item):
        retVal = []
        for recipe in self.recipes:
            if recipe[0] == item or recipe[1] == item or self.recipes[recipe] == item:
                retVal.append(recipe)
        return retVal

    def renderRecipes(self, known):
        print()
        counter = 0
        for recipe in sorted(self.recipes):
            if known and self.recipes[recipe] != UNKNOWN:
                print("{} + {} = {}".format(recipe[0], recipe[1], self.recipes[recipe]))
                counter += 1
            elif not known and self.recipes[recipe] == UNKNOWN:
                print("{} + {} = {}".format(recipe[0], recipe[1], self.recipes[recipe]))
                counter += 1
        print("\ndiscovered {} recipes".format(counter))

    def menu(self):
        print()
        print("What would you like to do:")
        print("\t(a)dd an item")
        print("\t(r)emove an item")
        print("\t(A)dd a recipe")
        print("\t(R)emove a recipe")
        print("\t(k)nown items")
        print("\t(K)nown recipes")
        print("\t(u)nknown recipes")
        print("\t(q)uit")

        data = msvcrt.getch().decode("utf-8")
        if data == "a": self.addItem()
        if data == "r": self.removeItem()
        if data == "A": self.addRecipe()
        if data == "R": self.removeRecipe()
        if data == "k": self.renderItems()
        if data == "K": self.renderRecipes(known = True)
        if data == "u" or data == "U": self.renderRecipes(known = False)
        if data == "q": return -1

        return 0

    def log(self, data, level = LEVEL_LOW): print("[{}] {}".format(level, data))

    def run(self):
        while True:
            ret = self.menu()
            if ret == -1: break
        self.save()

alchemy = Alchemy()
alchemy.run()
