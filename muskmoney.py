import yfinance as yf
import matplotlib.pyplot as plt

# 1. Configuration parameters
ticker_symbol = "SPCX"
musk_shares = 6.42e9  # 6.42 Billion Shares
ipo_date = "2026-06-12" 

# 2. Download daily market data
spcx_data = yf.download(ticker_symbol, start=ipo_date, interval="1d")

if not spcx_data.empty:
    # 3. Calculate Daily Equity Net Worth in Billions USD
    spcx_data['Net_Worth_Billion'] = (spcx_data['Close'] * musk_shares) / 1e9

    # 4. Generate Daily Net Worth Visualization
    plt.figure(figsize=(11, 5))
    plt.plot(spcx_data.index, spcx_data['Net_Worth_Billion'], color='#0052cc', linewidth=2, label="SpaceX Net Worth ($B)")
    
    # Add Trillionaire Marker Reference
    plt.axhline(y=1000, color='red', linestyle='--', alpha=0.5, label="$1 Trillion")

    # Chart Styling
    plt.title("Elon Musk's SpaceX Shares Worth", fontsize=13, fontweight='bold')
    plt.xlabel("Date", fontsize=11)
    plt.ylabel("Billions(USD)", fontsize=11)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc="upper right")
    plt.tight_layout()

    # Save and display chart
    plt.savefig("/home/jkdebian/vscode/muskmoney.png", dpi=300)
    plt.show()
else:
    print("Unable to fetch data for ticker symbol 'SPCX'. Check network connection or ticker status.")