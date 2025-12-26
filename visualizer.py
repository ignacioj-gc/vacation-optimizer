# visualize.py
from optimizer import VacationOptimizer
import calendar


def visualize_year(year, vacation_days, country, strategy):
    optimizer = VacationOptimizer(year, vacation_days, country, strategy=strategy)
    result = optimizer.optimize()

    vacation_set = set(result["vacation_days"])
    holiday_dates = {h["date"] for h in result["holidays"]}

    for month in range(1, 13):
        print(f"\n{calendar.month_name[month]} {year}")
        print("Mo Tu We Th Fr Sa Su")

        cal = calendar.monthcalendar(year, month)
        for week in cal:
            week_str = []
            for day in week:
                if day == 0:
                    week_str.append("  ")
                else:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    if date_str in vacation_set:
                        week_str.append(f"V{day:1d}")  # V for vacation
                    elif date_str in holiday_dates:
                        week_str.append(f"H{day:1d}")  # H for holiday
                    else:
                        week_str.append(f"{day:2d}")
            print(" ".join(week_str))


if __name__ == "__main__":
    # print('Original strategy:')
    # visualize_year(2025, 15, "PR", 'continuous')
    print('\nSpread strategy:')
    visualize_year(2025, 15, "PR", 'spread')
