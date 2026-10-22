"""Track stock positions and export a portfolio valuation to CSV.

Run with ``python portfolio.py``. Enter a ticker, purchase price, share
quantity, and current share price for each position; enter ``done`` when
finished. Current prices are entered manually so the script needs no external
services or third-party packages.
"""

import csv
import math
from datetime import datetime
from pathlib import Path


CSV_FIELDS = (
    "timestamp",
    "ticker",
    "shares",
    "buy_price",
    "current_price",
    "invested_value",
    "market_value",
    "gain_loss",
    "gain_loss_percent",
)


def prompt_positive_number(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
        except ValueError:
            print("Enter a valid number.")
            continue

        if not math.isfinite(value) or value <= 0:
            print("Enter a number greater than zero.")
            continue
        return value


def collect_positions() -> dict[str, dict[str, float]]:
    positions: dict[str, dict[str, float]] = {}
    print("Enter portfolio positions. Type 'done' when finished.")

    while True:
        ticker = input("Ticker: ").strip().upper()
        if ticker.lower() == "done":
            break
        if not ticker:
            print("Ticker cannot be blank.")
            continue
        if ticker in positions:
            print(f"{ticker} has already been entered; each ticker can be entered once.")
            continue

        buy_price = prompt_positive_number("Buy price per share: ")
        shares = prompt_positive_number("Number of shares: ")
        current_price = prompt_positive_number("Current price per share: ")
        positions[ticker] = {
            "buy_price": buy_price,
            "shares": shares,
            "current_price": current_price,
        }

    return positions


def build_summary(
    positions: dict[str, dict[str, float]], timestamp: str
) -> tuple[list[dict[str, str]], dict[str, float]]:
    rows: list[dict[str, str]] = []
    totals = {
        "invested_value": 0.0,
        "market_value": 0.0,
        "gain_loss": 0.0,
    }

    for ticker, position in positions.items():
        invested_value = position["buy_price"] * position["shares"]
        market_value = position["current_price"] * position["shares"]
        gain_loss = market_value - invested_value
        gain_loss_percent = gain_loss / invested_value * 100
        totals["invested_value"] += invested_value
        totals["market_value"] += market_value
        totals["gain_loss"] += gain_loss
        rows.append(
            {
                "timestamp": timestamp,
                "ticker": ticker,
                "shares": f"{position['shares']:.8f}".rstrip("0").rstrip("."),
                "buy_price": f"{position['buy_price']:.2f}",
                "current_price": f"{position['current_price']:.2f}",
                "invested_value": f"{invested_value:.2f}",
                "market_value": f"{market_value:.2f}",
                "gain_loss": f"{gain_loss:.2f}",
                "gain_loss_percent": f"{gain_loss_percent:.2f}",
            }
        )

    return rows, totals


def write_summary(
    rows: list[dict[str, str]], totals: dict[str, float], output_path: Path
) -> None:
    timestamp = rows[0]["timestamp"]
    total_percent = totals["gain_loss"] / totals["invested_value"] * 100
    total_row = {
        "timestamp": timestamp,
        "ticker": "PORTFOLIO TOTAL",
        "shares": "",
        "buy_price": "",
        "current_price": "",
        "invested_value": f"{totals['invested_value']:.2f}",
        "market_value": f"{totals['market_value']:.2f}",
        "gain_loss": f"{totals['gain_loss']:.2f}",
        "gain_loss_percent": f"{total_percent:.2f}",
    }

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
        writer.writerow(total_row)


def display_summary(
    rows: list[dict[str, str]], totals: dict[str, float]
) -> None:
    print()
    print(
        f"{'Ticker':<18} {'Shares':>12} {'Buy/share':>12} "
        f"{'Current/share':>15} {'Invested':>12} {'Value':>12} "
        f"{'Gain/Loss':>12} {'Return':>9}"
    )
    for row in rows:
        print(
            f"{row['ticker']:<18} {float(row['shares']):>12.4f} "
            f"${float(row['buy_price']):>11,.2f} "
            f"${float(row['current_price']):>14,.2f} "
            f"${float(row['invested_value']):>11,.2f} "
            f"${float(row['market_value']):>11,.2f} "
            f"${float(row['gain_loss']):>11,.2f} "
            f"{float(row['gain_loss_percent']):>8.2f}%"
        )

    total_percent = totals["gain_loss"] / totals["invested_value"] * 100
    print("-" * 106)
    print(
        f"{'PORTFOLIO TOTAL':<18} {'':>12} {'':>12} {'':>15} "
        f"${totals['invested_value']:>11,.2f} "
        f"${totals['market_value']:>11,.2f} "
        f"${totals['gain_loss']:>11,.2f} {total_percent:>8.2f}%"
    )


def main() -> None:
    positions = collect_positions()
    if not positions:
        print("No positions entered; no CSV file was created.")
        return

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    rows, totals = build_summary(positions, timestamp)
    display_summary(rows, totals)

    output_path = Path(__file__).resolve().with_name("portfolio_summary.csv")
    write_summary(rows, totals, output_path)
    print(f"\nSummary saved to: {output_path}")


if __name__ == "__main__":
    main()
