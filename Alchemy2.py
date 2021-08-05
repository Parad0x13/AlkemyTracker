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
        self.finalItems = []

        self.load()

    def load(self):
        f = open(self.filename, "r+")
        lines = f.read().splitlines()
        f.close()

        # The very first thing we need to do is create a listing of every item and recipe mentioned in the savefile
        itemsFound = []
        finalItemsFound = []
        recipesFound = {}
        for line in lines:
            a = re.split("\+|=", line)
            for n in range(len(a)): a[n] = a[n].strip()    # [TODO] Find a more elegant way of doing this...

            # Here we merge whatever item we found into all possible items
            if len(a) == 1: itemsFound += a

            # Here we account for any final items found
            if len(a) == 2:
                if a[1] == "final": finalItemsFound.append(a[0])
                else: self.log("There is an issue with the savefile on line {}".format(line), level = LEVEL_HIGH)

            # Here we account for any recipes found
            if len(a) == 3: recipesFound[(a[0], a[1])] = a[2]

            # Here we error check for any erronous data in the savefile
            assert len(a) == 1 or len(a) == 2 or len(a) == 3, "Incorrect data presented for line {}".format(line)

        # Ensure we have no duplicates
        itemsFound = list(set(itemsFound))
        itemsFound.sort()    # Not needed but I like it anyways

        # Now we add all our found items to our instance
        # This will create recipes for every possible item match
        for item in itemsFound: self.addItem(item)

        # Account for any final items we may have encountered
        for finalItem in finalItemsFound: self.finalItems.append(finalItem)

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

        for finalItem in self.finalItems:
            f.write("{} = final\n".format(finalItem))

        for recipe in self.recipes:
            a = recipe[0]
            b = recipe[1]
            c = self.recipes[recipe]
            for item in c:
                if item == UNKNOWN: continue    # There is no reason to save unknown combinations, it just inflates filesize
                f.write("{} + {} = {}\n".format(a, b, item))

        f.close()

    # This is accomplished by iterating through every recipe and finding all possible items
    def getItems(self):
        items = []

        for recipe in self.recipes:
            items.append(recipe[0])
            items.append(recipe[1])
            for item in self.recipes[recipe]: items.append(item)

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

            if " " in item:
                print("Spaces are not allowed in item names")
                return

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

        if item not in items and item not in self.finalItems:
            self.log("That item does not exist", level = LEVEL_MED)
            return

        if item in self.finalItems: self.finalItems.remove(item)
        recipes = self.getRecipesContainingItem(item)
        for recipe in recipes: self.removeRecipe(recipe[0], recipe[1])

    # Some items in the game are 'final' and do not mix with anything, this will automatically account for all possible combinations
    def finalizeItem(self, finalItem = None):
        if finalItem != None: print("Attempting to finalize item {}".format(finalItem))

        # Process user input
        if finalItem == None:
            print("Attempting to finalize a user specified item")

            item = input("Item name: ").strip()
            self.finalizeItem(item)

            return

        recipes = self.getRecipesContainingItem(finalItem)
        for recipe in recipes: self.removeRecipe(recipe[0], recipe[1])
        if finalItem not in self.finalItems:
            self.finalItems.append(finalItem)
            self.finalItems.sort()

    # If an item currently does not match with a single item already discovered we can mass account for it here
    def noCurrentMatches(self, unmatched = None):
        if unmatched != None: print("Attempting to unmatch {} against all currently discovered items".format(unmatched))

        # Process user input
        if unmatched == None:
            print("Attempting to unmatch a user specified item against all currently discovered items")

            item = input("Item name: ").strip()
            self.noCurrentMatches(item)

            return

        items = self.getItems()
        for item in items:
            self.addRecipe((item, unmatched), NOTHING)

    def renderItems(self):
        print()
        items = self.getItems()
        for item in items: print(item)
        for finalItem in self.finalItems: print("{} = final".format(finalItem))
        print("\ndiscovered {} items".format(len(items) + len(self.finalItems)))

    def addRecipe(self, inputs = None, output = None):
        if inputs != None and output != None: self.log("Attempting to add recipe {} + {} = {}".format(inputs[0], inputs[1], output))

        # Process user input
        if inputs == None and output == None:
            self.log("Attempting to add a user specified recipe")

            a = input("Item A: ").strip()

            # Allow for the option to write itemA itemB itemC instead of hitting enter three times
            line = a.split(" ")
            if len(line) == 3:
                a = line[0]
                b = line[1]
                c = line[2]
            else:
                b = input("Item B: ").strip()
                c = input("Output: ").strip()

            # Here we check if the user referenced any new items during the generation of this new recipe
            items = self.getItems()
            for item in [a, b, c]:
                if item not in items:
                    self.addItem(item)

            self.addRecipe((a, b), c)

            return

        assert inputs != None and output != None, "Error in addRecipe()"

        if UNKNOWN in inputs: return    # We don't want to process any recipes whose inputs are unknown
        if NOTHING in inputs: return    # We don't want to process any recipes whose inputs are nothing
        if "" in inputs: return    # Likewise we don't want to process recipes that have no item names

        # Here we ensure alphanumerics are upheld in the recipe
        # [TODO] Find a more elegant way of doing this, I don't like this method at all
        a = inputs[0]
        b = inputs[1]
        if b < a:
            a = inputs[1]
            b = inputs[0]

        if (a, b) in self.recipes and output in self.recipes[(a, b)]:
            self.log("Recipe already exists", level = LEVEL_MED)
            return

        if (a, b) not in self.recipes: self.recipes[(a, b)] = []
        self.recipes[(a, b)].append(output)

        if output != UNKNOWN:
            # Ensure we remove any recipes that have an unknown value since we now have a valid output
            if UNKNOWN in self.recipes[(a, b)]: self.removeRecipe((a, b), UNKNOWN)

    def removeRecipe(self, inputs = None, output = None):
        if inputs != None and output != None: self.log("Attempting to remove recipe {}, {}".format(inputs, output))

        # Process user input
        if inputs == None:
            a = input("Item A: ").strip()
            b = input("Item B: ").strip()
            c = input("Output: ").strip()
            self.removeRecipe((a, b), c)
            return

        assert inputs != None and output != None, "Error in addRecipe()"

        # Here we ensure alphanumerics are upheld in the recipe
        # [TODO] Find a more elegant way of doing this, I don't like this method at all
        a = inputs[0]
        b = inputs[1]
        if b < a:
            a = inputs[1]
            b = inputs[0]

        if output in self.recipes[(a, b)]:
            self.recipes[(a, b)].remove(output)
        if self.recipes[(a, b)] == []:    # In the event that there no longer exists any output for the removed output
            del self.recipes[(a, b)]

    def getRecipesContainingItem(self, item):
        retVal = []
        for inputs in self.recipes:
            for output in self.recipes[inputs]:
                if inputs[0] == item: retVal.append((inputs, output))
                elif inputs[1] == item: retVal.append((inputs, output))
                elif item == output: retVal.append((inputs, output))
        return retVal

    def renderRecipes(self, known):
        print()
        counter = 0
        for recipe in sorted(self.recipes):
            for item in self.recipes[recipe]:
                if known and item != UNKNOWN:
                    print("{} + {} = {}".format(recipe[0], recipe[1], item))
                    counter += 1
                elif not known and item == UNKNOWN:
                    print("{} + {} = {}".format(recipe[0], recipe[1], item))
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
        print("\t(f)inalize item")
        print("\t(n)o current matches")
        print("\t(q)uit")

        # try/except will handle errant keypresses like the up/down/left/right keys
        try:
            data = msvcrt.getch().decode("utf-8")
            if data == "a": self.addItem()
            if data == "r": self.removeItem()
            if data == "A": self.addRecipe()
            if data == "R": self.removeRecipe()
            if data == "k": self.renderItems()
            if data == "K": self.renderRecipes(known = True)
            if data == "u" or data == "U": self.renderRecipes(known = False)
            if data == "f": self.finalizeItem()
            if data == "n": self.noCurrentMatches()
            if data == "q": return -1
        except: pass

        return 0

    def log(self, data, level = LEVEL_LOW): print("[{}] {}".format(level, data))

    def run(self):
        while True:
            ret = self.menu()
            self.save()
            if ret == -1: break

alchemy = Alchemy()
alchemy.run()
