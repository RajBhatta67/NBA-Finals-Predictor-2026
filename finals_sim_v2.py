"""
NBA Finals Series Simulator v2 - Data-Driven Edition
------------------------------------------------------
Knicks lead Spurs 3-1 in the 2026 NBA Finals. Game 5 tonight in San Antonio.

WHAT'S NEW vs v1:
v1 used a made-up win probability (NYK_BASE_WIN_PROB = 0.45).
v2 calculates win probability from REAL data: each team's Offensive and
Defensive Rating (points scored/allowed per 100 possessions) from games
1, 2, and 4 of this actual series.

THE MODEL:
1. Net Rating = Offensive Rating - Defensive Rating (how dominant a team
   was, per 100 possessions, independent of pace)
2. Average each team's Net Rating across the series so far
3. Convert the Net Rating DIFFERENCE between teams into a win probability
   using a logistic curve - the same general approach real analytics sites
   (like FiveThirtyEight's NBA model) use
4. Add a home-court adjustment (NBA home teams average ~+3 net rating boost
   historically)

import random
import math


# STEP 1: Real net ratings from ALL 4 games of this series so far

# Format: (NYK_off_rating, NYK_def_rating), in chronological order
game_data = [
    (104.04, 95.96),    # Game 1 (NYK won 105-95 @ SAS)
    (101.70, 103.09),   # Game 2 (NYK won 105-104 @ SAS)
    (112.48, 114.91),   # Game 3 (NYK lost 111-115 vs SAS, at home)
    (109.95, 111.81),   # Game 4 (NYK won 107-106 vs SAS, at home)
]

nyk_net_ratings = [off - dfn for off, dfn in game_data]

# --- Recency weighting ---
# Instead of a plain average, give more recent games more influence.
# DECAY < 1 means older games matter less. With DECAY = 0.7, game 4
# (most recent) counts ~1.43x as much as game 3, ~2x as much as game 2, etc.
DECAY = 0.7
n = len(nyk_net_ratings)
weights = [DECAY ** (n - 1 - i) for i in range(n)]  # most recent game gets weight 1.0

weighted_sum = sum(w * r for w, r in zip(weights, nyk_net_ratings))
NYK_AVG_NET_RATING = weighted_sum / sum(weights)
SAS_AVG_NET_RATING = -NYK_AVG_NET_RATING

# For comparison: plain unweighted average
plain_avg = sum(nyk_net_ratings) / n

print(f"Per-game NYK net ratings: {[round(x,2) for x in nyk_net_ratings]}")
print(f"Plain average (all games equal):     {plain_avg:+.2f}")
print(f"Recency-weighted average (decay={DECAY}): {NYK_AVG_NET_RATING:+.2f}")
print(f"  -> weights used (oldest to newest): {[round(w,3) for w in weights]}\n")


# STEP 2: Convert net rating differential -> win probability
# Logistic function: as the rating gap grows, win probability approaches
# 0 or 1, but never quite gets there (anything can happen on a given night).
#
# SCALE controls how "swingy" small rating differences are. ~10-12 is
# typical for translating NBA net ratings to single-game win probabilities.

SCALE = 11.0
HOME_COURT_RATING_BOOST = 3.0  # NBA home court ~= +3 net rating, per studies

def game_win_prob(home_team):
    """Return probability the KNICKS win, given who's home."""
    nyk_rating = NYK_AVG_NET_RATING
    sas_rating = SAS_AVG_NET_RATING

    if home_team == "NYK":
        nyk_rating += HOME_COURT_RATING_BOOST
    else:
        sas_rating += HOME_COURT_RATING_BOOST

    diff = nyk_rating - sas_rating  # positive favors Knicks
    # logistic curve maps diff -> probability between 0 and 1
    prob_nyk = 1 / (1 + math.exp(-diff / SCALE))
    return prob_nyk


# STEP 3: Simulate one possible "rest of series
def simulate_series():
    nyk_wins, sas_wins = 3, 1
    schedule = [("Game 5", "SAS"), ("Game 6", "NYK"), ("Game 7", "SAS")]
    knicks_won_game5 = None

    for game_name, home_team in schedule:
        if nyk_wins == 4 or sas_wins == 4:
            break
        p_nyk = game_win_prob(home_team)
        if random.random() < p_nyk:
            nyk_wins += 1
            if game_name == "Game 5":
                knicks_won_game5 = True
        else:
            sas_wins += 1
            if game_name == "Game 5":
                knicks_won_game5 = False

    winner = "NYK" if nyk_wins == 4 else "SAS"
    return winner, nyk_wins + sas_wins, knicks_won_game5



# STEP 4: Run the simulation many times and tally
def run_simulation(num_trials=50000):
    results = {
        "NYK_in_5": 0, "NYK_in_6": 0, "NYK_in_7": 0,
        "SAS_in_6": 0, "SAS_in_7": 0,
        "knicks_win_tonight": 0, "knicks_win_title_overall": 0,
    }
    for _ in range(num_trials):
        winner, games_played, won_g5 = simulate_series()
        if won_g5:
            results["knicks_win_tonight"] += 1
        if winner == "NYK":
            results["knicks_win_title_overall"] += 1
        key = f"{winner}_in_{games_played}"
        if key in results:
            results[key] += 1
    return results, num_trials


def print_report(results, num_trials):
    def pct(x):
        return f"{100 * x / num_trials:.1f}%"

    print("=" * 55)
    print("NBA FINALS SIMULATION v2 - DATA-DRIVEN (Knicks lead 3-1)")
    print(f"Tonight's Game 5 win prob (model): NYK {pct(results['knicks_win_tonight'])}")
    print("=" * 55)
    print(f"\nKnicks win the title OVERALL: {pct(results['knicks_win_title_overall'])}")
    print(f"Spurs force a Game 7:          {pct(results['SAS_in_6'] + results['SAS_in_7'])}")
    print("\nBreakdown:")
    print(f"  Knicks win in 5: {pct(results['NYK_in_5'])}")
    print(f"  Knicks win in 6: {pct(results['NYK_in_6'])}")
    print(f"  Knicks win in 7: {pct(results['NYK_in_7'])}")
    print(f"  Spurs win in 7:  {pct(results['SAS_in_7'])}")


if __name__ == "__main__":
    results, n = run_simulation()
    print_report(results, n)

    print("\n" + "=" * 55)
    print("COMPARISON: Vegas odds had SAS at 64% / NYK at 36% for Game 5.")
    print("Our data-driven model says NYK has roughly "
          f"{100*game_win_prob('SAS'):.1f}% in San Antonio tonight.")


    # EXTRA 1: Decay sensitivity sweep

    # How sensitive is our prediction to the DECAY parameter?
    # A robust model shouldn't swing wildly for small parameter changes.
    print("\n" + "=" * 55)
    print("SENSITIVITY: Game 5 win prob (NYK, in San Antonio) by DECAY value")
    print("=" * 55)
    for test_decay in [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        w = [test_decay ** (len(nyk_net_ratings) - 1 - i) for i in range(len(nyk_net_ratings))]
        avg = sum(wi * r for wi, r in zip(w, nyk_net_ratings)) / sum(w)
        diff = (avg - HOME_COURT_RATING_BOOST) - (-avg)  # NYK away, SAS home
        p = 1 / (1 + math.exp(-diff / SCALE))
        note = "  <- equal weighting" if test_decay == 1.0 else ""
        print(f"  DECAY={test_decay:.1f}: NYK net rating={avg:+.2f}, Game 5 win prob={100*p:.1f}%{note}")


    # EXTRA 2: Bootstrap confidence interval
    
    # We only have 4 games of data - that's a TINY sample. The "average net
    # rating" we computed could easily be off by a lot just due to random
    # game-to-game variance. Bootstrapping = resample our 4 games (with
    # replacement) thousands of times to see the RANGE of plausible averages.
    print("\n" + "=" * 55)
    print("UNCERTAINTY: Bootstrap 90% confidence interval on NYK net rating")
    print("=" * 55)
    boot_avgs = []
    for _ in range(10000):
        sample = [random.choice(nyk_net_ratings) for _ in nyk_net_ratings]
        boot_avgs.append(sum(sample) / len(sample))
    boot_avgs.sort()
    low = boot_avgs[int(0.05 * len(boot_avgs))]
    high = boot_avgs[int(0.95 * len(boot_avgs))]
    print(f"  With only {len(nyk_net_ratings)} games of data, NYK's true net rating")
    print(f"  could plausibly be anywhere from {low:+.2f} to {high:+.2f}.")
    print("  This is WHY single-model predictions should come with a grain of salt -")
    print("  small sample sizes mean a lot of uncertainty, even with real data.")


    # EXTRA 3: "What if" scenario - star player impact(Daddy Brunson)

    # Estimate a player's impact on team net rating using their plus/minus
    # or efficiency, then see how the title probability shifts if they're
    # limited (e.g. foul trouble, minor injury).
    print("\n" + "=" * 55)
    print("WHAT-IF: Impact of a net rating swing (e.g. star player limited)")
    print("=" * 55)
    for swing in [-5, -3, 0, +3, +5]:
        adjusted_nyk = NYK_AVG_NET_RATING + swing
        adjusted_sas = -NYK_AVG_NET_RATING  # Spurs unaffected

        # Quick re-simulation with adjusted rating
        orig = NYK_AVG_NET_RATING
        NYK_AVG_NET_RATING = adjusted_nyk
        SAS_AVG_NET_RATING = -adjusted_nyk
        temp_results, temp_n = run_simulation(num_trials=5000)
        title_prob = 100 * temp_results["knicks_win_title_overall"] / temp_n
        NYK_AVG_NET_RATING = orig
        SAS_AVG_NET_RATING = -orig

        label = f"NYK net rating {swing:+d}"
        print(f"  {label:18s} -> Title probability: {title_prob:.1f}%")

    print("\nTry plugging in a real number: if a key player's on/off net rating")
    print("split (findable on basketball-reference) is -6, that's your 'swing'.")
