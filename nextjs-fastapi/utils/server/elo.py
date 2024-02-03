from __future__ import division

def expected(A, B):
    """
    Calculate expected score of A in a match against B

    :param A: Elo rating for player A
    :param B: Elo rating for player B
    """
    return 1 / (1 + 10 ** ((B - A) / 400))


def elo(old, exp, score, k=32):
    """
    Calculate the new Elo rating for a player

    :param old: The previous Elo rating
    :param exp: The expected score for this match
    :param score: The actual score for this match
    :param k: The k-factor for Elo (default: 32)
    """
    return old + k * (score - exp)

def calculate_new_elo(player_elo, opponent_elo, result):
    """
    Calculate new elo for each player based on the result

    :param player_elo: Elo rating for the player
    :param opponent_elo: Elo rating for the opponent
    :param result: The result of the match
    """
    expected_score = expected(player_elo, opponent_elo)
    if result == "win":
        return elo(player_elo, expected_score, 1)
    elif result == "loss":
        return elo(player_elo, expected_score, 0)
    else:
        return elo(player_elo, expected_score, 0.5)
    
    