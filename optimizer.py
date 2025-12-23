from datetime import date, timedelta
from typing import List, Dict, Set, Tuple
import holidays

# from app import app


class VacationOptimizer:
    def __init__(self, year: int, vacation_days: int, country: str = 'PR', blackout_dates: List[str] = []):
        self.year = year
        self.vacation_days = vacation_days
        self.country = country
        self.blackout_dates = set(blackout_dates) if blackout_dates else set()

        try:
            holiday_obj = holidays.country_holidays(country, years=year)
            # Convert to a simple dict immediately to avoid serialization issues
            self.holidays = {date: name for date, name in holiday_obj.items()}
            self.holiday_dates = set(str(d) for d in self.holidays.keys())
        except (KeyError, AttributeError):
            # Fallback to PR holidays if country not found
            holiday_obj = holidays.country_holidays('PR', years=year)
            self.holidays = {date: name for date, name in holiday_obj.items()}
            self.holiday_dates = set(str(d) for d in self.holidays.keys())

        self.allocated_vacation = set()


    def is_workday(self, d: date) -> bool:
        date_str = str(d)
        return (
            d.weekday() < 5 and
            date_str not in self.holiday_dates and
            date_str not in self.blackout_dates and
            date_str not in self.allocated_vacation
        )
    

    def is_off_day(self, d: date) -> bool:
        date_str = str(d)
        return (
            d.weekday() >= 5 or
            date_str in self.holiday_dates or
            date_str in self.allocated_vacation
        )
    

    def calculate_streak_length(self, start_date: date, vacation_dates: Set[str]) -> int:
        """
        Calculates the length of consecutive days off work starting from start_date
        
        :param start_date: Description
        :type start_date: date
        :param vacation_dates: Description
        :type vacation_dates: Set[str]
        :return: Description
        :rtype: int
        """
        temp_vacation = self.allocated_vacation.union(vacation_dates)

        current = start_date
        while current >= date(self.year, 1, 1):
            prev_date = current-timedelta(days=1)
            if prev_date < date(self.year, 1, 1):
                break
            date_str = str(prev_date)
            if prev_date.weekday() < 5 and date_str not in self.holiday_dates and date_str not in temp_vacation:
                break
            current = prev_date

        streak_start = current
        streak_end = current

        current = streak_start
        year_end = date(self.year, 12, 31)

        while current <= year_end:
            date_str = str(current)
            if current.weekday() < 5 and date_str not in self.holiday_dates and date_str not in temp_vacation:
                break
            streak_end = current
            current += timedelta(days=1)

        return (streak_end - streak_start).days + 1
    

    def find_best_placement(self, remaining_days: int) -> Tuple[List[str], float]:
        """
        Finds the best placement for vacation days.
        
        :param self: Description
        :param remaining_days: Description
        :type remaining_days: int
        :return: Description
        :rtype: Tuple[List[str], float]
        """
        best_placement = []
        best_score = 0

        current_date = date(self.year, 1, 1)
        year_end = date(self.year, 12, 31)

        while current_date <= year_end:
            if not self.is_workday(current_date):
                current_date += timedelta(days=1)
                continue

            for length in range(1, min(remaining_days + 1, 11)):
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

                if streak_length >= 9:
                    efficiency *= 1.1
                if streak_length >= 14:
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

        while current_date <= year_end:
            if self.is_off_day(current_date):
                streak_start = current_date
                streak_dates = []

                while current_date <= year_end and self.is_off_day(current_date):
                    date_str = str(current_date)
                    day_type = 'weekend' if current_date.weekday() >= 5 else (
                        'holiday' if date_str in self.holiday_dates else 'vacation'
                    )
                    streak_dates.append({
                        'date': date_str,
                        'type': day_type
                    })
                    current_date += timedelta(days=1)

                if len(streak_dates) >= 2:
                    streaks.append({
                        'start': str(streak_start),
                        'end': str(current_date - timedelta(days=1)),
                        'length': len(streak_dates),
                        'dates': streak_dates
                    })

            else:
                current_date += timedelta(days=1)

        return streaks
    

    def optimize(self) -> Dict:
        """
        Main optimization method using greedy algorithms.
        Returns complete optimization results.
        """

        remaining  = self.vacation_days
        iterations = 0
        max_iterations = 100

        while remaining > 0 and iterations < max_iterations:
            placement, score = self.find_best_placement(remaining)

            if not placement or score == 0:
                #If no good placements are found, just use remaining days on random workdays.
                current_date = date(self.year, 1, 1)

                while remaining > 0 and current_date <= date(self.year, 12, 31):
                    if self.is_workday(current_date):
                        self.allocated_vacation.add(str(current_date))
                        remaining -= 1
                    current_date += timedelta(days=1)
                break

            for day in placement:
                self.allocated_vacation.add(day)

            remaining -= len(placement)
            iterations += 1
        
        streaks = self.calculate_streaks()
        total_days_off = sum(streak['length'] for streak in streaks)

        sorted_vacation = sorted(list(self.allocated_vacation))

        efficiency = total_days_off / self.vacation_days if self.vacation_days > 0 else 0

        return {
            'vacation_days': sorted_vacation,
            'vacation_days_used': len(sorted_vacation),
            'streaks': streaks,
            'total_days_off': total_days_off,
            'efficiency': round(efficiency, 2),
            'year': self.year,
            'country': self.country,
            'holidays': [{'date': str(d), 'name': name} for d, name in self.holidays.items()] if self.holidays else []
        }