from threading import Timer

# First attempt to create a list with alements that are automatically deleted
class TimedList:
    def __init__(self, item_lifetime=30) -> None:
        self.item_lifetime = item_lifetime
        self.items = []
        self.timer = Timer(item_lifetime, self.auto_remove)

    def auto_remove(self):
        if len(self.items) > 0:
            self.items.pop()
    
    def add(self, item):
        self.items.append(item)
        if not self.timer.is_alive():
            self.timer = Timer(self.item_lifetime, self.auto_remove)

    def remove(self, item):
        if item not in self.items:
            return
        self.items.remove(item)
        if self.timer.is_alive():
            self.timer.cancel()
        if len(self.items) > 0:
            self.timer.cancel()
            self.timer = Timer(self.item_lifetime, self.auto_remove)

    def size(self):
        return len(self.items)

    def index(self, item):
        return self.items.index(item)

    