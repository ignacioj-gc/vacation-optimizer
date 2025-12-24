# test_edge_cases.py
from optimizer import VacationOptimizer


def test_edge_cases():
    # Test with 0 vacation days
    try:
        result = VacationOptimizer(2025, 0, "PR").optimize()
        assert result["vacation_days_used"] == 0
        print("✓ Handles 0 vacation days")
    except:
        print("✗ Failed with 0 vacation days")

    # Test with many vacation days
    try:
        result = VacationOptimizer(2025, 50, "PR").optimize()
        assert result["vacation_days_used"] <= 50
        print("✓ Handles 50 vacation days")
    except:
        print("✗ Failed with 50 vacation days")

    # Test with blackout dates
    try:
        result = VacationOptimizer(
            2025, 15, "PR", blackout_dates=["2025-12-24", "2025-12-26"]
        ).optimize()
        assert "2025-12-24" not in result["vacation_days"]
        assert "2025-12-26" not in result["vacation_days"]
        print("✓ Respects blackout dates")
    except:
        print("✗ Failed with blackout dates")


if __name__ == "__main__":
    test_edge_cases()
