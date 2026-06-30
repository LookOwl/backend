from dataclasses import dataclass


@dataclass
class ResultPage:
    starts_at : int
    number_of_results : int
