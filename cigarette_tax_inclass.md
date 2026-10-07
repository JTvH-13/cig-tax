# In-Class Problem: Who Paid California's \$2 Cigarette Tax?

**The question:** On April 1, 2017, California's Prop 56 raised the state cigarette tax from \$0.87 to \$2.87 a pack. Who paid the \$2, smokers or sellers? How much less did Californians buy? What did the tax cost in lost surplus, and could the state have raised more with a bigger tax?

**Format:** teams of three, one shared GitHub repo, about 45 minutes. Each person owns one script, works on their own branch, and gets it into `main` through a pull request that a teammate reviews.

**Using Claude:** use Claude Code for the code and the git commands. Two rules: the answers in your `answers/` file are written by you, not Claude, and the team questions at the end are **no AI**.

---

## The data (CDC, not FRED)

*The Tax Burden on Tobacco, 1970–2019* (Orzechowski and Walker), on the CDC's open data portal. One row per state, year and measure, 15,300 rows. No API key:

```python
URL = "https://data.cdc.gov/resource/7nwe-3aj9.csv?$limit=50000"
```

Keep `$limit=50000`: without it the portal returns only the first 1,000 rows.

| `submeasuredesc` | Column name in `data/clean.csv` | Units |
|---|---|---|
| Average Cost per pack | `price` | dollars, including excise taxes |
| Cigarette Consumption (Pack Sales Per Capita) | `packs_pc` | packs per person per year |
| State Tax per pack | `state_tax` | dollars |
| Gross Cigarette Tax Revenue | `revenue` | dollars, state only |

---

## Roles

| | Person A: Data | Person B: Estimates | Person C: Model |
|---|---|---|---|
| Owns | `get_data.py`, `data/clean.csv` | `estimate.py`, `results/estimates.json`, `figs/packs.png` | `model.py`, `results/model.json` |
| Branch | `data` | `estimates` | `model` |
| Reviews | B's pull request | C's pull request | A's pull request |
| Writes | `answers/A.md` | `answers/B.md` | `answers/C.md` |

Never edit a file another person owns. Two people changing the same file is how you get a merge conflict.

---

## Step 1: Set up the repo (Person A, 5 minutes)

Everyone: send Person A your GitHub username.

Person A makes a folder (`mkdir cig-tax && cd cig-tax`) with three files in it, then puts it on GitHub:

- `README.md`: paste the roles table and the file contract below, plus an empty **Decisions** section.
- `predictions.md`: the team's predictions (no AI): of the \$2, how many cents showed up in the price smokers paid? By what percent did pack sales fall?
- `.gitignore` with two lines, `data/raw/` and `.DS_Store`. The raw download is about 4 MB and anyone can re-download it, so it stays out of the repo. `.DS_Store` files are Mac clutter that cause pointless merge conflicts.

```bash
git init -b main
git add . && git commit -m "Spec and predictions"
gh repo create cig-tax --private --source=. --push
gh api -X PUT repos/A_USERNAME/cig-tax/collaborators/B_USERNAME
gh api -X PUT repos/A_USERNAME/cig-tax/collaborators/C_USERNAME
```

Persons B and C: accept the invite at `github.com/A_USERNAME/cig-tax/invitations`, then:

```bash
gh repo clone A_USERNAME/cig-tax && cd cig-tax
```

**File contract** (goes in README.md):

- `data/clean.csv`: one row per state and year; columns `state, year, price, packs_pc, state_tax, revenue`.
- `results/estimates.json`: keys `q0, p0, passthrough, elasticity` (California, before the tax).
- `results/model.json`: the numbers in C's table.

## Step 2: Work on your branch (everyone at once, about 25 minutes, including reviews)

The git loop for every branch (you can type these or ask Claude Code to run them, but know what each does):

```bash
git switch -c BRANCHNAME              # once, before you start
git add FILES && git commit -m "..."  # as you go
git push -u origin BRANCHNAME         # put the branch on GitHub
gh pr create --fill                   # open the pull request
git switch main && git pull           # get what teammates merged
git switch BRANCHNAME && git merge main --no-edit   # bring it into your branch
```

(`--no-edit` stops git from opening a text editor for the merge message. If you end up in the vim editor anyway, type `:q` and press Enter; the merge still goes through.)

Before you open a pull request, run your script from scratch and check it works.

### Person A: data and timing

1. `get_data.py` downloads the data, saves it unmodified to `data/raw/`, pivots it into `data/clean.csv` per the contract, and prints California's rows for 2014–2019. Check you got all 15,300 raw rows.
2. Look at the California rows and work out the timing (no AI for this step):
   - **A1.** In which year does California's price first jump? Pack sales first fall sharply? Revenue first rise?
   - **A2.** Revenue rose only 28% from 2016 to 2017, even though the tax more than tripled. Then it nearly doubled in 2018. What period must "2017" cover for revenue and pack sales? What about price? (If "2017" meant January to December, nine of its twelve months would be at the new rate.)
3. Add your before and after years to the **Decisions** section of README.md: one pair for price, one pair for pack sales. They are not the same years. B uses them. Then push and open your pull request **right away**, because B is waiting on `clean.csv` and the Decisions.
4. **A3.** Now ask Claude what "year" means for each measure in this dataset. Did it agree with what you found? Which do you trust?

Write A1–A3 in `answers/A.md`. If your first pull request has already been merged, put the answers on a new branch (`git switch main && git pull && git switch -c data-answers`) and open a second pull request. C reviews it the same way.

### Person B: pass-through and elasticity

Write `estimate.py` from the contract while A works. Test it once A's pull request is merged: commit your work, then `git switch main && git pull`, then `git switch estimates && git merge main --no-edit`.

1. **Control states:** states whose state tax per pack was the same in every year from 2015 to 2019.
2. **Pass-through:** the change in California's price between A's price years, divided by \$2. Then subtract the control states' average price change and recompute. Save the second one as `passthrough`.
3. **Elasticity:** the log change in California's pack sales divided by the log change in its price (naive). Then subtract the control states' average log changes from both before dividing (difference-in-differences). Save the second one as `elasticity`, with California's before-tax `q0` and `p0`.
4. **Chart:** pack sales per person, 2005–2019, California against the control average, both indexed to 2016 = 100. Add a line at 2017, a title that states the finding, axis labels and a source note. Save it as `figs/packs.png`.

In `answers/B.md`:

- **B1.** How many control states are there? Report both pass-through numbers and both elasticities.
- **B2.** Why is the difference-in-differences elasticity smaller in absolute value than the naive one?

### Person C: the model

Write `model.py` while A and B work. Until B's pull request is merged, put these placeholder numbers in a dictionary at the top of `model.py`: `q0 = 20, p0 = 6, elasticity = -0.5, passthrough = 0.9`. **Don't create `results/estimates.json` yourself.** It's B's file. Once B's pull request is in `main`, merge `main` into your branch (the last two lines of the git loop) and switch to reading the JSON.

1. **Calibrate.** For straight-line demand, the elasticity at $(q_0, p_0)$ is $-\frac{1}{d_1}\frac{p_0}{q_0}$, and the share of a per-unit tax paid by buyers is $\frac{d_1}{d_1 + s_1}$. Choose $d_1$ to match `elasticity` and $s_1$ to match `passthrough`, then $d_0$ and $s_0$ so both curves pass through $(q_0, p_0)$.
2. **Solve.** For the tax $t = 2$, use `brentq` to find the quantity where the buyers' price minus the sellers' price equals $t$. Compute consumer and producer surplus with `quad`. Compute the deadweight loss separately, as the area between the demand and supply curves from the after-tax quantity to the before-tax quantity (also with `quad`). Report per person: quantity, buyers' and sellers' prices (the "sellers' price" here is the price before the new \$2 is added, so it still includes the old taxes), change in CS, change in PS, revenue, and deadweight loss. Then check that ΔCS + ΔPS + revenue + DWL = 0. If it doesn't, something is wrong.
3. **Bigger tax?** Use `minimize_scalar` to find the new tax (on top of the old ones) that maximizes its revenue $t \cdot q(t)$. Check it against $(d_0 - s_0)/2$.

In `answers/C.md`:

- **C1.** Your table from step 2, using B's real estimates.
- **C2.** Where is California's \$2 compared with the revenue-maximizing tax? What does the pass-through say about the slope of supply?

## Step 3: Review and merge (as soon as each pull request opens)

Don't save reviews for the end. A's pull request has to be merged by about minute 15, or B and C are stuck.

Review the pull request in your row of the roles table. Commit your own work first, so that switching branches can't mix your changes into theirs. Don't approve it until you've run it yourself:

```bash
gh pr list
gh pr checkout NUMBER
python THEIR_SCRIPT.py          # does it run? do the numbers make sense?
gh pr review NUMBER --approve -b "Ran it; I get ..."   # quote one number
gh pr merge NUMBER --merge
git restore .                    # throw away the files their script regenerated
git switch YOUR_BRANCH           # back to your own work
```

Person C, reviewing A: also check the Decisions years against the California rows. If they're wrong, every number B and C produce is wrong too.

If something's wrong, use `gh pr review NUMBER --request-changes -b "..."` instead of approving and merging (then `git restore .` and switch back as above). The author pushes a fix to the same branch, and you review again. Merge order: A, then B, then C.

## Step 4: Team questions (no AI, 8 minutes)

One person runs `git switch main && git pull`, writes `answers/team.md`, then commits and pushes it to `main`.

- **T1.** Compare the results with `predictions.md`. Which prediction was furthest off?
- **T2.** The data measures **pack sales** in California, not smoking by Californians. Give two reasons the drop in pack sales could overstate how much Californians cut back. Which way does each push the elasticity, and so the deadweight loss?
- **T3.** Paste the output of `git log --oneline --graph`.

**If you finish early:** replace C's straight-line demand with constant-elasticity demand $q = A p^{\varepsilon}$, using B's elasticity and choosing $A$ so it passes through $(q_0, p_0)$. Keep C's supply curve. Run the same `minimize_scalar` search with bounds (0, 10), then (0, 50), and explain what happens.

Before you submit, Person A adds the instructor as a collaborator (`gh api -X PUT repos/A_USERNAME/cig-tax/collaborators/INSTRUCTOR_USERNAME`), since the repo is private. Submit the repo link.
