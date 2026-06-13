# NBA Finals Win Probability Model

A Monte Carlo simulator that estimates series outcomes using real box-score
data, then compares its predictions to Vegas odds and quantifies its own
uncertainty.

**Context:** Built during Game 5 of the 2026 NBA Finals (Knicks lead Spurs 3-1).

## What it does

1. Pulls each team's **Net Rating** (Offensive Rating − Defensive Rating)
   from every game of the series so far.
2. Computes a **recency-weighted average** — recent games count more than
   early ones, since team performance trends over a series.
3. Converts the net rating gap into a **win probability** using a logistic
   function (the same general approach used by real NBA analytics models),
   with a home-court adjustment.
4. Runs **50,000 Monte Carlo simulations** of the remaining games to get
   series-outcome probabilities (win in 5/6/7, etc.).
5. Compares the model's prediction to actual Vegas odds and investigates
   the gap.
6. Runs a **decay sensitivity sweep** to check the model isn't overly
   sensitive to its one tunable parameter.
7. Computes a **bootstrap 90% confidence interval** on the net rating
   estimate — with only 4 games of data, the estimate has real uncertainty,
   and the model says so honestly.
8. Includes a **"what-if" tool**: plug in a net-rating swing (e.g. a star
   player's on/off impact if they're injured/in foul trouble) and see how
   title probability shifts.

## Results (as of Game 5)

| Metric | Value |
|---|---|
| NYK net rating, plain average | +0.60 |
| NYK net rating, recency-weighted (decay=0.7) | -0.58 |
| Model's Game 5 win prob (NYK, away) | ~40% |
| Vegas Game 5 line (NYK, away) | 36% |
| Model's title probability for NYK | ~84% |
| Bootstrap 90% CI on NYK net rating | [-2.14, +3.35] |

**Key finding:** recency-weighting moved the model's prediction from 46%
(plain average) to 40% — much closer to Vegas's 36% — because the Spurs
have been trending upward over the series. This suggests recent form
matters more than series-long averages for short-term predictions.

## How to run

```bash
python3 finals_sim_v2.py
```

No dependencies beyond the Python standard library.

## What I'd add next

- Pull net ratings across the *entire* playoff run for both teams (bigger
  sample = tighter confidence interval)
- Test recency weighting against multiple past playoff series to see if
  decay=0.7 generalizes or was a one-series fluke
- Incorporate rest days / travel distance between games
- Build a small Elo-style rating system that updates after each game,
  rather than recomputing from scratch

## Why I built this

I wanted to understand how sports analytics models actually work — not by
trusting a black-box prediction, but by building a simple one myself,
seeing where it disagrees with the market, and figuring out why. The
uncertainty quantification (bootstrap CI) ended up being the most important
part: a model is only useful if you know how much to trust it.
