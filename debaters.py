class Debater:
    def __init__(self, name, turn, debate_value, language_zone, optional=False, committed=False):
        self.name = name
        self.turn = turn
        self.debate_value = debate_value
        self.language_zone = language_zone
        self.optional = optional
        self.committed = committed

# Define language zones
GERMAN = "German"
ENGLISH = "English"
CATHOLIC = "Catholic"
FRENCH = "French"

# List of all debaters
debaters = [
    # German Protestant debaters
    Debater("Oekolompidus", 2, 2, GERMAN),
    Debater("Zwingli", 2, 3, GERMAN),
    Debater("Carlstadt", 1, 1, GERMAN),
    Debater("Luther", 1, 4, GERMAN),
    Debater("Bullinger", 3, 2, GERMAN),
    Debater("Melanchthon", 1, 3, GERMAN),
    Debater("Bucer", 1, 2, GERMAN),
    
    # Catholic debaters (purple cards)
    Debater("Campeggio", 1, 2, CATHOLIC),
    Debater("Eck", 1, 3, CATHOLIC),
    Debater("Tetzel", 1, 1, CATHOLIC),
    Debater("Contarini", 2, 2, CATHOLIC),
    Debater("Cajetan", 1, 1, CATHOLIC),
    Debater("Aleander", 1, 2, CATHOLIC),
    Debater("Caraffa", 5, 2, CATHOLIC),
    Debater("Canisius", 6, 3, CATHOLIC),
    Debater("Loyola", 6, 4, CATHOLIC),
    Debater("Pole", 5, 3, CATHOLIC),
    Debater("Faber", 6, 3, CATHOLIC),
    Debater("Gardiner", 7, 3, CATHOLIC),
    
    # English reformers (red cards)
    Debater("Knox", 6, 3, ENGLISH),
    Debater("Tyndale", 2, 2, ENGLISH),
    Debater("Wishart", 6, 1, ENGLISH),
    Debater("Latimer", 4, 1, ENGLISH, True),
    Debater("Cranmer", 4, 3, ENGLISH, True),
    Debater("Coverdale", 4, 2, ENGLISH, True),
    
    # Other reformers (blue cards)
    Debater("Cop", 4, 2, FRENCH),
    Debater("Calvin", 4, 4, FRENCH),
    Debater("Olivetan", 4, 1, FRENCH),
    Debater("Farel", 4, 2, FRENCH)
]

# Example usage:
if __name__ == "__main__":
    # Print all Catholic debaters
    print("Catholic Debaters:")
    for debater in [d for d in debaters if d.language_zone == CATHOLIC]:
        print(f"{debater.name}: Value {debater.debate_value}, Turn {debater.turn}")
    
    # Print all debaters with value 4
    print("\nDebaters with value 4:")
    for debater in [d for d in debaters if d.debate_value == 4]:
        print(f"{debater.name} ({debater.language_zone})")