import random


WORDS = (
    "python",
    "hangman",
    "terminal",
    "program",
    "keyboard",
    "developer",
    "function",
)

MAX_MISTAKES = 6

HANGMAN_STAGES = (
    """
     +---+
     |   |
         |
         |
         |
         |
    =======
    """,
    """
     +---+
     |   |
     O   |
         |
         |
         |
    =======
    """,
    """
     +---+
     |   |
     O   |
     |   |
         |
         |
    =======
    """,
    """
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =======
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
         |
         |
    =======
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
    /    |
         |
    =======
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
    / \\  |
         |
    =======
    """,
)


def display_word(word, guessed_letters):
    """Return the word with unguessed letters replaced by underscores."""
    normalized_word = str(word).lower()
    normalized_guesses = {str(letter).lower() for letter in guessed_letters}
    return " ".join(letter.upper() if letter in normalized_guesses else "_" for letter in normalized_word)


def play_game(word=None):
    """Play the game and return True if the player wins, otherwise False."""
    selected_word = random.choice(WORDS) if word is None else str(word).lower()
    guessed_letters = set()
    mistakes = 0

    print("Welcome to Hangman!")

    while mistakes < MAX_MISTAKES:
        print(HANGMAN_STAGES[mistakes])
        print(f"Word: {display_word(selected_word, guessed_letters)}")
        if guessed_letters:
            print(f"Guessed letters: {' '.join(sorted(letter.upper() for letter in guessed_letters))}")
        print(f"Incorrect guesses remaining: {MAX_MISTAKES - mistakes}")

        guess = input("Guess a letter: ").strip().lower()
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single letter.")
            continue
        if guess in guessed_letters:
            print("You already guessed that letter. Try another.")
            continue

        guessed_letters.add(guess)
        if guess not in selected_word:
            mistakes += 1
            print(f"Sorry, '{guess.upper()}' is not in the word.")
        elif all(letter in guessed_letters for letter in selected_word):
            print(HANGMAN_STAGES[mistakes])
            print(f"Word: {display_word(selected_word, guessed_letters)}")
            print(f"You win! The word was {selected_word.upper()}.")
            return True

    print(HANGMAN_STAGES[MAX_MISTAKES])
    print(f"You lose! The word was {selected_word.upper()}.")
    return False


if __name__ == "__main__":
    play_game()
