class LeagueMatchmaker:
    """
    Handles Elo/Glicko ratings and matchmaking for the agent population.
    """

    def __init__(self, k_factor: int = 32):
        self.ratings = {}  # model_id -> float
        self.k_factor = k_factor

    def update_ratings(self, model_a: str, model_b: str, score_a: float):
        # score_a: 1.0 for win, 0.5 for draw, 0.0 for loss
        ra = self.ratings.get(model_a, 1200.0)
        rb = self.ratings.get(model_b, 1200.0)

        expected_a = 1.0 / (1.0 + 10 ** ((rb - ra) / 400.0))
        new_ra = ra + self.k_factor * (score_a - expected_a)

        self.ratings[model_a] = new_ra
        # Symmetric update for rb...
        expected_b = 1.0 - expected_a
        self.ratings[model_b] = rb + self.k_factor * ((1.0 - score_a) - expected_b)
