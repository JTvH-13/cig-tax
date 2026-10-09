| | Person A: Data | Person B: Estimates | Person C: Model |
| --- | --- | --- | --- |
| Owns | `get_data.py`, `data/clean.csv` | `estimate.py`, `results/estimates.json`, `figs/packs.png` | `model.py`, `results/model.json` |
| Branch | `data` | `estimates` | `model` |
| Reviews | B's pull request | C's pull request | A's pull request |
| Writes | `answers/A.md` | `answers/B.md` | `answers/C.md` |

- `data/clean.csv`: one row per state and year; columns `state, year, price, packs_pc, state_tax, revenue`.
- `results/estimates.json`: keys `q0, p0, passthrough, elasticity` (California, before the tax).
- `results/model.json`: the numbers in C's table.

BEFORE AND AFTER TAX INCREASE:
raw rows: 15300
clean rows: 2550
     state  year  price  packs_pc  state_tax      revenue
California  2014  5.475      22.7       0.87  757512960.0
California  2015  5.607      22.3       0.87  754358820.0
California  2016  5.607      22.0       0.87  748095546.0
California  2017  7.659      20.5       2.87  956712690.0
California  2018  7.862      16.6       2.87 1887613448.0
California  2019  8.141      15.8       2.87 1791254942.0