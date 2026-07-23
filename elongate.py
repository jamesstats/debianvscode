import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd

# 1. Define the tickers and the timeframe
tickers = ["TSLA", "SPCX"]
start_date = "2026-06-12"
end_date = "2026-07-23"  # Requested inclusive end date

# yfinance treats the `end` parameter as exclusive. To include `end_date`
# in the downloaded range, add one day to the end date.
end_date_inclusive = (pd.to_datetime(end_date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

print(f"Downloading data from {start_date} to {end_date} (inclusive)...")

try:
    # 2. Download the historical Adjusted Close prices
    # Use 'Close' since 'Adj Close' may not be available for all tickers
    downloaded = yf.download(tickers, start=start_date, end=end_date_inclusive)
    
    # Extract Close data from MultiIndex columns
    if isinstance(downloaded.columns, pd.MultiIndex):
        data = downloaded.loc[:, "Close"]
    else:
        data = downloaded["Close"]

    # Drop any rows with missing data to ensure a clean alignment
    data = data.dropna()

    # 3. Calculate cumulative percentage returns
    # We divide every row by the first row (the baseline) and subtract 1
    # Formula: ((Price_t / Price_baseline) - 1) * 100
    returns = (data / data.iloc[0] - 1) * 100

    # 4. Plot the results
    plt.figure(figsize=(10, 6))

    # Plot Tesla (TSLA)
    plt.plot(
        returns.index,
        returns["TSLA"],
        label="Tesla (TSLA)",
        color="#cc0000",
        linewidth=2,
        marker="s",
    )

    # Plot SpaceX (SPCX)
    plt.plot(
        returns.index,
        returns["SPCX"],
        label="SpaceX (SPCX)",
        color="#121314",
        linewidth=2,
        marker="o",
    )

    # 5. Format and beautify the chart
    plt.title(
        f"SPACE vs TSLA: {start_date}",
        fontsize=14,
        fontweight="bold",
        pad=15,
        loc="left" 
    )
    plt.xlabel(" ", fontsize=11)
    plt.ylabel("Return (%)", fontsize=11)

    # Add a horizontal line at 0% to clearly show gains vs. losses
    plt.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.7)

    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(fontsize=11, loc="best")
    plt.gcf().autofmt_xdate()  # Cleanly format the dates on the X-axis
    plt.savefig("/home/jkdebian/vscode/space_vs_tsla.png", dpi=720, bbox_inches="tight")

    # Show the final plot window
    plt.tight_layout()

    plt.show()  

except Exception as e:
    print(f"An error occurred: {e}") 