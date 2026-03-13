import random

class Prober:
    def __init__(self):
        self.vibe_bank = [
            "A dark mode login screen with email/password fields and transparent background",
            "A profile card with an avatar, name and Follow Button",
            "A search bar that shows a 'No results' text when typed in",
            "A counter component with big '+' and '-' buttons",
            "A toggle switches that changes background color"
        ]

    def get_challenges(self,n=3):
        return random.sample(self.vibe_bank, n)

    