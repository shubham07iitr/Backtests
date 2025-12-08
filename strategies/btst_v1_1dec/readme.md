# BTST V1 - December 1st Run

## Strategy Logic
Buy ATM CE when evening spot > morning spot, else buy ATM PE

## Parameters
- Capital: $100,000
- Risk per day: 1% 
- Morning Time: 09:16
- Evening Time: 15:20
- Entry Time: 15:20
- Exit Time (Next Day): 09:16

## Results
- CAGR: 8.87%
- Max DD: -6.09%
- Win Rate: 51.48%
- Total Trades: 779

## Usage
run main.py using 
```bash
python3 main.py
```
## Notes
- First version of BTST strategy
- Update config.py for different entry and exit time variations