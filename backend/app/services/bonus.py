from typing import List
from datetime import date
from decimal import Decimal

class BonusOverRule:
    def __init__(self, threshold_percent: int, bonus_amount: Decimal):
        self.threshold_percent = threshold_percent
        self.bonus_amount = bonus_amount

def calc_projection(today: date, month_days: int, value_to_date: Decimal) -> Decimal:
    if today.day == 0:
        return value_to_date
    avg_per_day = value_to_date / today.day
    return avg_per_day * month_days

def calc_bonus_with_overachievement(plan: Decimal, fact: Decimal, base_bonus: Decimal,
                                   over_rules: List[BonusOverRule]) -> Decimal:
    result = Decimal(0)
    if plan and fact >= plan:
        result += base_bonus
        percent = (fact / plan) * Decimal(100)
        for r in sorted(over_rules, key=lambda x: x.threshold_percent):
            if percent >= r.threshold_percent:
                result += r.bonus_amount
    return result
