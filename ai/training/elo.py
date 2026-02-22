import math
from typing import Tuple


class EloSystem:
    def __init__(self, k_factor: int = 32):
        self.k_factor = k_factor

    def calculate_expected_score(self, rating_a: float, rating_b: float) -> float:
        return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

    def update_ratings(self, rating_a: float, rating_b: float, score_a: float) -> Tuple[float, float]:
        """
        score_a: 1.0 for win, 0.5 for draw, 0.0 for loss
        """
        expected_a = self.calculate_expected_score(rating_a, rating_b)
        expected_b = 1 - expected_a
        
        score_b = 1 - score_a
        
        new_rating_a = rating_a + self.k_factor * (score_a - expected_a)
        new_rating_b = rating_b + self.k_factor * (score_b - expected_b)
        
        return new_rating_a, new_rating_b

class Glicko2System:
    # Placeholder for more advanced rating system
    pass
