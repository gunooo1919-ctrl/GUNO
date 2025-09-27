# Simulator sederhana alokasi uang
def simulate_cashflow(income, needs, wants, savings):
    return {
        "Income": income,
        "Needs": income * needs,
        "Wants": income * wants,
        "Savings": income * savings
    }
