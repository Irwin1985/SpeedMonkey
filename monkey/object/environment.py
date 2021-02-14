class Environment:
    def __init__(self):
        self.store = {}
        self.outer = None

    def get(self, name):
        result = self.store.get(name)

        if result is None and self.outer is not None:
            result = self.outer.get(name)

        return result

    def set(self, name, val):
        self.store[name] = val


# Instance method
def new_enclosed_environment(outer):
    env = Environment()
    env.outer = outer
    return env