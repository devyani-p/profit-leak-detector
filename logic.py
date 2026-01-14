# logic.py
from rules import THRESHOLDS


def compute_metrics(
    units_sold: int,
    price: float,
    cost: float,
    discount_pct: float,
    return_pct: float,
    avg_stock_units: int,
    storage_cost_per_unit: float
):
    revenue = units_sold * price

    gross_profit = units_sold * (price - cost)

    # discount loss (simple: discount % of revenue)
    discount_loss = revenue * (discount_pct / 100.0)

    # return loss (simple: returned % of revenue)
    return_loss = revenue * (return_pct / 100.0)

    # inventory holding cost (simple monthly storage cost)
    inventory_cost = avg_stock_units * storage_cost_per_unit

    true_profit = gross_profit - discount_loss - return_loss - inventory_cost

    gross_margin_pct = (gross_profit / revenue * 100.0) if revenue > 0 else 0.0

    return {
        "revenue": revenue,
        "gross_profit": gross_profit,
        "discount_loss": discount_loss,
        "return_loss": return_loss,
        "inventory_cost": inventory_cost,
        "true_profit": true_profit,
        "gross_margin_pct": gross_margin_pct,
    }


def detect_leaks(metrics: dict):
    leaks = []

    revenue = metrics.get("revenue", 0) or 0
    gross_profit = metrics.get("gross_profit", 0) or 0

    # Over-discounting
    discount_pct_est = (metrics["discount_loss"] / revenue * 100) if revenue else 0
    if discount_pct_est > THRESHOLDS["max_discount_pct"]:
        leaks.append(("Over-discounting", metrics["discount_loss"]))

    # High returns
    return_pct_est = (metrics["return_loss"] / revenue * 100) if revenue else 0
    if return_pct_est > THRESHOLDS["max_return_pct"]:
        leaks.append(("High returns", metrics["return_loss"]))

    # Inventory holding too high (simple heuristic)
    if gross_profit > 0 and metrics["inventory_cost"] > 0.10 * gross_profit:
        leaks.append(("Inventory holding too high", metrics["inventory_cost"]))

    # Low margin / pricing risk
    if metrics["gross_margin_pct"] < THRESHOLDS["min_gross_margin_pct"]:
        leaks.append(("Low margin / pricing risk", gross_profit))

    leaks.sort(key=lambda x: x[1], reverse=True)
    return leaks


def recommend_actions(leaks):
    actions = []
    for name, _amount in leaks:
        if name == "Over-discounting":
            actions.append("Cap discount closer to 10–12% unless discounts clearly increase volume enough to offset it.")
        elif name == "High returns":
            actions.append("Track top return reasons and fix the biggest 1–2 causes (quality checks, sizing info, packaging).")
        elif name == "Inventory holding too high":
            actions.append("Reduce slow-moving stock; reorder in smaller batches; target lower average inventory.")
        elif name == "Low margin / pricing risk":
            actions.append("Try a small price increase or negotiate supplier costs; aim for 25%+ gross margin.")
    return actions
