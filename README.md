# IBKR TWS read-only connectivity probe

This repository currently contains a small Python probe for the Interactive Brokers Trader Workstation (TWS) API.

## What it does

`tws_read_only_probe.py` connects to TWS at `127.0.0.1:7496` with client ID `73`, requests account summary, positions, and executions, waits up to 25 seconds, then disconnects. It does not place, amend, or cancel orders.

The program prints account and trading data to the terminal. Run it only in an environment where that output is appropriate to view and store.

## Requirements

- Python 3.10 or newer
- The Interactive Brokers `ibapi` Python package
- TWS running locally with API access enabled

Install the API package using the installation instructions supplied with your IBKR TWS/API version. Then run:

```powershell
python .\tws_read_only_probe.py
```

The host, port, client ID, and timeout are currently set in the script.
