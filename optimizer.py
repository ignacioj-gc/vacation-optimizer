from datetime import date, timedelta
from typing import List, Dict, Set, Tuple, Literal
import holidays


_strategy_options = Literal["spread", "continuous"]


class VacationOptimizer:
    def __init__(
        self,
        year: int,
        vacation_days: int,
        country: str = "PR",
        blackout_dates: List[str] = [],
        custom_holidays: List[str] = [],
        exclude_holidays: List[str] = [],
        strategy: _strategy_options = "spread",
    ):
        self.year = year
        self.vacation_days = vacation_days
        self.country = country
        self.blackout_dates = set(blackout_dates) if blackout_dates else set()
        self.strategy = strategy

        try:
            holiday_obj = holidays.country_holidays(country, years=year)
            # Convert to a simple dict immediately to avoid serialization issues
            self.holidays = {date: name for date, name in holiday_obj.items()}
            self.holiday_dates = set(str(d) for d in self.holidays.keys())
        except (KeyError, AttributeError):
            # Fallback to PR holidays if country not found
            holiday_obj = holidays.country_holidays("PR", years=year)
            self.holidays = {date: name for date, name in holiday_obj.items()}
            self.holiday_dates = set(str(d) for d in self.holidays.keys())

        self.allocated_vacation = set()

    def is_workday(self, d: date, check_adjacent: bool = False) -> bool:
        date_str = str(d)
        is_valid_workday = (
            d.weekday() < 5
            and date_str not in self.holiday_dates
            and date_str not in self.blackout_dates
            and date_str not in self.allocated_vacation
        )
        if self.strategy == 'spread' and is_valid_workday and check_adjacent:
            return not self.is_adjacent_to_vacation(d)
        
        return is_valid_workday

    def is_off_day(self, d: date) -> bool:
        date_str = str(d)
        return (
            d.weekday() >= 5
            or date_str in self.holiday_dates
            or date_str in self.allocated_vacation
        )
    
    def is_adjacent_to_vacation(self, d: date) -> bool:
        """Check if a date is adjacent to already-allocated vacation days, skipping weekends."""
        
        # Find previous workday
        prev_day = d - timedelta(days=1)
        days_checked = 0
        while (prev_day >= date(self.year, 1, 1) and 
            prev_day.weekday() in {5, 6} and 
            days_checked < 7):  # Safety: max 7 days back
            prev_day -= timedelta(days=1)
            days_checked += 1
        
        # Find next workday  
        next_day = d + timedelta(days=1)
        days_checked = 0
        while (next_day <= date(self.year, 12, 31) and 
            next_day.weekday() in {5, 6} and 
            days_checked < 7):  # Safety: max 7 days forward
            next_day += timedelta(days=1)
            days_checked += 1
        
        # Only check if we found a valid workday
        prev_is_vacation = (prev_day >= date(self.year, 1, 1) and 
                            prev_day.weekday() < 5 and
                            str(prev_day) in self.allocated_vacation)
        
        next_is_vacation = (next_day <= date(self.year, 12, 31) and 
                            next_day.weekday() < 5 and
                            str(next_day) in self.allocated_vacation)
        
        return prev_is_vacation or next_is_vacation
        

    def calculate_streak_length(
        self, start_date: date, vacation_dates: Set[str]
    ) -> int:
        """
        Calculates the length of consecutive days off work starting from start_date

        :param start_date: Starting date of the days off range
        :type start_date: date
        :param vacation_dates: Dates included in the streak range
        :type vacation_dates: Set[str]
        :return: Length of consecutive days off
        :rtype: int
        """
        temp_vacation = self.allocated_vacation.union(vacation_dates)

        current = start_date
        while current >= date(self.year, 1, 1):
            prev_date = current - timedelta(days=1)
            if prev_date < date(self.year, 1, 1):
                break
            date_str = str(prev_date)
            if (
                prev_date.weekday() < 5
                and date_str not in self.holiday_dates
                and date_str not in temp_vacation
            ):
                break
            current = prev_date

        streak_start = current
        streak_end = current

        current = streak_start
        year_end = date(self.year, 12, 31)

        while current <= year_end:
            date_str = str(current)
            if (
                current.weekday() < 5
                and date_str not in self.holiday_dates
                and date_str not in temp_vacation
            ):
                break
            streak_end = current
            current += timedelta(days=1)

        return (streak_end - streak_start).days + 1

    def find_best_placement(self, remaining_days: int, no_checks: bool = False) -> Tuple[List[str], float]:
        """
        Finds the best placement for vacation days based on selected strategy.

        :param remaining_days: Available vacation days remaining
        :type remaining_days: int
        :param no_checks: Disable checking if new vacation is adjacent to another vacation day
        :type no_checks: bool
        :return: Returns a list of vacation dates and the total efficiency of this placement
        :rtype: Tuple[List[str], float]
        """

        best_placement = []
        best_score = 0

        current_date = date(self.year, 1, 1)
        year_end = date(self.year, 12, 31)
        
        # CRITICAL: Set max block size based on strategy
        if self.strategy == 'spread':
            max_block_size = min(remaining_days + 1, 4)  # Max 3 vacation days per block
        else:  # continuous
            max_block_size = min(remaining_days + 1, 11)  # Can use up to 10 days

        while current_date <= year_end:             

            no_checks = (
                self.strategy == 'spread' and
                not no_checks and
                len(self.allocated_vacation) > 0
            )

            if not self.is_workday(current_date, check_adjacent=no_checks):
                current_date += timedelta(days=1)
                continue

            for length in range(1, max_block_size):
                vacation_dates = []
                test_date = current_date

                while len(vacation_dates) < length and test_date <= year_end:
                    if self.is_workday(test_date):
                        vacation_dates.append(str(test_date))
                    test_date += timedelta(days=1)

                if len(vacation_dates) < length:
                    break

                vacation_set = set(vacation_dates)
                streak_length = self.calculate_streak_length(current_date, vacation_set)
                efficiency = streak_length / len(vacation_dates)

                # Bonus for creating very long streaks (continuous strategy)
                if self.strategy == 'continuous':
                    if streak_length >= 9:
                        efficiency *= 1.1
                    if streak_length >= 14:
                        efficiency *= 1.2

                # Bonus for shorter blocks (spread strategy)
                if self.strategy == 'spread' and len(vacation_dates) <= 2:
                    efficiency *= 1.2

                if efficiency > best_score:
                    best_score = efficiency
                    best_placement = vacation_dates

            current_date += timedelta(days=1)

        return best_placement, best_score

    def calculate_streaks(self) -> List[Dict]:
        """Calculate all consecutive day-off streaks in the year."""
        streaks = []
        current_date = date(self.year, 1, 1)
        year_end = date(self.year, 12, 31)
        
        day_count = 0
        while current_date <= year_end:
            day_count += 1
            
            date_str = str(current_date)
            
            # Simple check without calling is_off_day
            is_weekend = current_date.weekday() >= 5
            is_holiday = date_str in self.holiday_dates
            is_vacation = date_str in self.allocated_vacation
            
            if is_weekend or is_holiday or is_vacation:
                # Start of a streak
                streak_start = current_date
                streak_dates = []
                
                # Collect consecutive off days
                while current_date <= year_end:
                    date_str = str(current_date)
                    is_weekend = current_date.weekday() >= 5
                    is_holiday = date_str in self.holiday_dates
                    is_vacation = date_str in self.allocated_vacation
                    
                    if not (is_weekend or is_holiday or is_vacation):
                        break  # End of streak
                    
                    day_type = 'weekend' if is_weekend else ('holiday' if is_holiday else 'vacation')
                    streak_dates.append({
                        'date': date_str,
                        'type': day_type
                    })
                    current_date += timedelta(days=1)
                
                if len(streak_dates) >= 2:
                    streaks.append({
                        'start': str(streak_start),
                        'end': str(streak_dates[-1]['date']),
                        'length': len(streak_dates),
                        'dates': streak_dates
                    })
            else:
                current_date += timedelta(days=1)
        
        return streaks

    def optimize(self) -> Dict:
        """
        Heuristic-based optimization for spreading vacation throughout the year.
        """
        remaining = self.vacation_days
        
        # Phase 1: Fill 1-day gaps
        for holiday_date in sorted(self.holidays.keys()):
            if remaining <= 0:
                break
            
            if holiday_date.weekday() == 3:  # Thursday
                friday = holiday_date + timedelta(days=1)
                if self.is_workday(friday, check_adjacent=False) and str(friday) not in self.allocated_vacation:
                    self.allocated_vacation.add(str(friday))
                    remaining -= 1
            
            elif holiday_date.weekday() == 1:  # Tuesday
                monday = holiday_date - timedelta(days=1)
                if self.is_workday(monday, check_adjacent=False) and str(monday) not in self.allocated_vacation:
                    self.allocated_vacation.add(str(monday))
                    remaining -= 1
                
        # Phase 2: Extend 3-day weekends
        for holiday_date in sorted(self.holidays.keys()):
            if remaining <= 0:
                break
            
            if holiday_date.weekday() == 0:  # Monday
                friday = holiday_date - timedelta(days=3)
                if self.is_workday(friday, check_adjacent=False) and str(friday) not in self.allocated_vacation:
                    self.allocated_vacation.add(str(friday))
                    remaining -= 1
            
            elif holiday_date.weekday() == 4:  # Friday
                monday = holiday_date + timedelta(days=3)
                if self.is_workday(monday, check_adjacent=False) and str(monday) not in self.allocated_vacation:
                    self.allocated_vacation.add(str(monday))
                    remaining -= 1                
        # Skip phases 3 and 4 for now - they might have bugs
        
        # Phase 5: Simplified greedy
        if remaining > 0:
            # Just place remaining days anywhere
            current_date = date(self.year, 1, 1)
            count = 0
            while remaining > 0 and current_date <= date(self.year, 12, 31):
                if self.is_workday(current_date, check_adjacent=False):
                    self.allocated_vacation.add(str(current_date))
                    remaining -= 1
                    count += 1
                current_date += timedelta(days=1)
        
        streaks = self.calculate_streaks()
        total_days_off = sum(streak['length'] for streak in streaks)
        sorted_vacation = sorted(list(self.allocated_vacation))
        efficiency = total_days_off / self.vacation_days if self.vacation_days > 0 else 0

        return {
            "vacation_days": sorted_vacation,
            "vacation_days_used": len(sorted_vacation),
            "streaks": streaks,
            "total_days_off": total_days_off,
            "efficiency": round(efficiency, 2),
            "year": self.year,
            "country": self.country,
            "strategy": self.strategy,
            "holidays":[{'date': str(d), 'name': name} for d, name in sorted(self.holidays.items())]
        }
