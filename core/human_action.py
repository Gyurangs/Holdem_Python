class HumanAction:
    def __init__(self):
        # action: "fold" | "call" | "raise"
        self.action = None
        self.amount = 0

    def set(self, action, amount=0):
        self.action = action
        self.amount = amount

    def consume(self):
        action = self.action
        amount = self.amount
        self.action = None
        self.amount = 0
        return action, amount

    def ready(self):
        return self.action is not None
    
    def reset(self):
        self.action = None
        self.amount = 0
