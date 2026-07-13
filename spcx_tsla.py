import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import yfinance as yf

# ============================================
# TICKER COMPARISON: SPCX vs TSLA
# ============================================

# Fetch data starting from June 22, 2026
start_date = "2026-06-12"
end_date = "2026-07-13"  # Requested inclusive end date

# yfinance treats the `end` parameter as exclusive. To include `end_date`,
# add one day and use that as the `end` argument.
end_date_inclusive = (pd.to_datetime(end_date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

try:
    spcx = yf.download("SPCX", start=start_date, end=end_date_inclusive, progress=False)
    tsla = yf.download("TSLA", start=start_date, end=end_date_inclusive, progress=False)

    # Check data structure and handle appropriately
    if spcx.empty or tsla.empty:
        print("Warning: One or both tickers returned no data.")
        print(f"SPCX data shape: {spcx.shape}")
        print(f"TSLA data shape: {tsla.shape}")
    else:
        # Handle MultiIndex columns from yfinance
        spcx_close = spcx[("Close", "SPCX")] if ("Close", "SPCX") in spcx.columns else spcx["Close"]
        tsla_close = tsla[("Close", "TSLA")] if ("Close", "TSLA") in tsla.columns else tsla["Close"]
        
        # Flatten spcx/tsla close into Series if they're DataFrames
        if isinstance(spcx_close, pd.DataFrame):
            spcx_close = spcx_close.iloc[:, 0]
        if isinstance(tsla_close, pd.DataFrame):
            tsla_close = tsla_close.iloc[:, 0]
        
        # Reset indices and create a clean comparison
        spcx_reset = pd.DataFrame({
            "Date": spcx.index,
            "SPCX_Close": spcx_close.values
        })
        tsla_reset = pd.DataFrame({
            "Date": tsla.index,
            "TSLA_Close": tsla_close.values
        })
        
        # Calculate daily percentage change
        spcx_reset["SPCX_Return"] = spcx_reset["SPCX_Close"].pct_change() * 100
        tsla_reset["TSLA_Return"] = tsla_reset["TSLA_Close"].pct_change() * 100
        
        # Merge on Date
        comparison = pd.merge(spcx_reset, tsla_reset, on="Date")
        
        # Print summary
        print("=" * 80)
        print("TICKER COMPARISON: SPCX vs TSLA (Starting June 22, 2026)")
        print("=" * 80)
        print(comparison.to_string(index=False))
        print("\n" + "=" * 80)
        print("SUMMARY STATISTICS")
        print("=" * 80)
        
        spcx_start = float(spcx_close.iloc[0])
        spcx_end = float(spcx_close.iloc[-1])
        tsla_start = float(tsla_close.iloc[0])
        tsla_end = float(tsla_close.iloc[-1])
        
        spcx_return_total = ((spcx_end / spcx_start) - 1) * 100
        tsla_return_total = ((tsla_end / tsla_start) - 1) * 100
        
        print(f"\nSPCX (Starting Price: ${spcx_start:.2f}, Ending Price: ${spcx_end:.2f})")
        print(f"  Avg Daily Return: {spcx_reset['SPCX_Return'].mean():.2f}%")
        print(f"  Total Return: {spcx_return_total:.2f}%")

        print(f"\nTSLA (Starting Price: ${tsla_start:.2f}, Ending Price: ${tsla_end:.2f})")
        print(f"  Avg Daily Return: {tsla_reset['TSLA_Return'].mean():.2f}%")
        print(f"  Total Return: {tsla_return_total:.2f}%")
        
        print(f"\nBetter Performer: {'SPCX' if spcx_return_total > tsla_return_total else 'TSLA'}")
        print(f"Difference: {abs(spcx_return_total - tsla_return_total):.2f}%")

        # Plot comparison
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))

        # Plot 1: Closing Prices
        axes[0].plot(comparison["Date"], comparison["SPCX_Close"], label="SPCX", marker="o", linewidth=2, color="blue")
        axes[0].plot(comparison["Date"], comparison["TSLA_Close"], label="TSLA", marker="s", linewidth=2, color="red")
        axes[0].set_title("Daily Closing Prices: SPCX vs TSLA", fontsize=14, fontweight="bold")
        axes[0].set_ylabel("Price ($)", fontsize=11)
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # Plot 2: Daily Returns
        x_pos = range(len(comparison) - 1)
        width = 0.35
        axes[1].bar([i - width/2 for i in x_pos], comparison["SPCX_Return"][1:].values, 
                    label="SPCX", alpha=0.7, width=width, color="blue")
        axes[1].bar([i + width/2 for i in x_pos], comparison["TSLA_Return"][1:].values, 
                    label="TSLA", alpha=0.7, width=width, color="red")
        axes[1].set_title("Daily Percentage Change: SPCX vs TSLA", fontsize=14, fontweight="bold")
        axes[1].set_ylabel("Daily Return (%)", fontsize=11)
        axes[1].set_xlabel("Trading Day", fontsize=11)
        axes[1].set_xticks(x_pos)
        axes[1].set_xticklabels([f"Day {i+1}" for i in x_pos])
        axes[1].legend()
        axes[1].grid(True, alpha=0.3, axis="y")
        axes[1].axhline(y=0, color="black", linestyle="-", linewidth=0.8)

        plt.tight_layout()
        plt.savefig("/home/jkdebian/vscode/spcx_tsla.png", dpi=300, bbox_inches="tight")
        print("\n✅ Chart saved as 'ticker_comparison.png'")
        plt.show()

except Exception as e:
    print(f"Error fetching ticker data: {e}")
    import traceback
    traceback.print_exc()
    print("Note: This may occur if the tickers or dates are not available.")

# ============================================
# MAMDANI POLLING ANALYSIS
# ============================================

