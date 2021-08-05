import re
import msvcrt

UNKNOWN = "?"

class Alchemy:
    def __init__(self):
        self.recipes = []
        self.loadSave()

    def loadSave(self):
        filename = "savefile.txt"

        f = open(filename, "r+")
        lines = f.read().splitlines()

        # First we need to iterate through and find every possible item/recipe available
        itemsFound = []
        recipesFound = []
        for line in lines:
            a = re.split('\+|=', line)
            for n in range(len(a)): a[n] = a[n].strip()    # [TODO] Find a more elegant way of doing this...

            # Here we merge lists to account for all possible items
            itemsFound += a

            # Here we account for existing recipes
            if len(a) == 3: recipesFound.append(tuple(a))

            # Here we error check for any erronous data in the savefile
            assert len(a) == 1 or len(a) == 3, "Incorrect data presented for line {}".format(line)

        """
        # Now we create all possible connections between items taking into account existing recipes
        for a in range(len(itemsFound)):
            for b in range(a, len(itemsFound)):
                c = itemsFound[a]
                d = itemsFound[b]

                # Ensure we don't overwrite a recipe if it already exists
                recipeExists = False
                for recipe in recipesFound:
                    if recipe[0:2] == (c, d): recipeExists = True
                if recipeExists: continue

                recipesFound.append((c, d, UNKNOWN))

        recipesFound = list(set(recipesFound))
        recipesFound.sort()
        self.recipes = recipesFound
        """

        itemsFound = list(set(itemsFound))
        for item in itemsFound:
            self.addItem(item)

        recipesFound = list(set(recipesFound))
        #recipesFound.sort()
        #self.recipes = recipesFound
        for recipe in recipesFound:
            self.addRecipe(recipe)

    def renderItems(self):
        items = self.getItems()
        for item in items: print(item)

    def renderRecipes(self, known):
        print()
        for recipe in self.recipes:
            if known and recipe[2] != UNKNOWN:
                print("{} + {} = {}".format(recipe[0], recipe[1], recipe[2]))
            elif not known and recipe[2] == UNKNOWN:
                print("{} + {} = {}".format(recipe[0], recipe[1], recipe[2]))

    def getItems(self):
        found = []
        for recipe in self.recipes:
            found.append(recipe[0])
            found.append(recipe[1])
            found.append(recipe[2])
        found = list(set(found))
        found.sort()

        try: found.remove(UNKNOWN)
        except: pass

        return found

    def addItem(self, name):
        print("Adding {}".format(name))
        items = self.getItems()

        if name in items:
            print("That item already exists!")
            return

        self.addRecipe((name, name, UNKNOWN))
        for item in items: self.addRecipe((item, name, UNKNOWN))

    # [TODO] Sanity check and ensure that recipes can be a + b = c OR b + a = c
    def addRecipe(self, recipe = None):
        # In the event that a user is inputing the recipe manually
        if recipe == None:
            a = input("Item A: ")
            b = input("Plus item B: ")
            c = input("Equals item: ")
            #self.addRecipe((a, b, c))

            self.addItem(a)
            self.addItem(b)
            self.addItem(c)

            self.addRecipe((a, b, c))

            return

        # Here we just sort the two input values by alpha so they are standardized... for now!
        # This is a VERY VERY VERY dumb way of doing this...
        # [TODO] Fix this nonsense
        a = recipe[0]
        b = recipe[1]
        c = recipe[2]
        if b < a: recipe = (b, a, c)

        self.recipes.append(recipe)
        self.recipes.sort()

        if (a, b, c) in self.recipes:
            print("Has redundant")

        # Now we make sure any existing recipe that equated to UNKNOWN is removed
        # [TODO] Do this the right way... not this a, b | b, a nonsense
        #try:
        #    self.recipes.remove((a, b, UNKNOWN))
        #    self.recipes.remove((b, a, UNKNOWN))
        #except: pass

    def menu(self):
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
        if data == "c": self.addRecipe()
        if data == "i": self.renderItems()
        if data == "u": self.renderRecipes(known = False)
        if data == "l": self.renderRecipes(known = True)
        if data == "q": return -1

        return 0

    def run(self):
        while True:
            ret = self.menu()
            if ret == -1: break

        print("\nSaving File...")

alchemy = Alchemy()
alchemy.run()
