# 📈 Elo Rating System Foundations

This directive codifies the principles of the Elo rating system, which serves as the primary engine for calculating relative team strength and win probabilities in the PRO BALL PREDICTOR terminal.

## 🏁 Definition & Overview
The **Elo rating system**, created by Hungarian-American physics professor Arpad Elo, is a method for calculating relative skill levels in zero-sum games.
- **Goal**: To predict the expected outcome of a match between two entities.
- **Symmetry**: If two teams have equal ratings, each is expected to win 50% of the time.

## ⚙️ How It Works
### 1. Expected Score
The probability of Team A winning against Team B is calculated using the formula:
$$\text{Expected Score} = \frac{1}{1 + 10^{\frac{\text{Rating}_B - \text{Rating}_A}{400}}}$$

- **100 Point Delta**: ~64% win probability.
- **200 Point Delta**: ~76% win probability.

### 2. Rating Adjustment (K-Factor)
After a game, ratings are updated based on the delta between the **Actual Score** (1 for win, 0.5 for draw, 0 for loss) and the **Expected Score**.
$$\text{New Rating} = \text{Old Rating} + K \times (\text{Actual Score} - \text{Expected Score})$$

- **K-Factor**: Determines the sensitivity of the system. 
  - *High K*: Fast adjustments (better for early season/new data).
  - *Low K*: Stability (better for established veterans/late season).
  - *PRO BALL PREDICTOR Default*: `4.0` (as defined in `core/config.py`).

## 🏅 Rating Categories (Traditional Reference)
While originally for chess, the tiers equate to competitive categories:
- **Below 1200**: Beginner / Rebuilding (e.g., replacement-level teams).
- **1200–1600**: Casual/Club (League Average is 1500).
- **1600–2000**: Intermediate/Competitive (Playoff contenders).
- **2000–2200**: Candidate Master (Elite / Divisional leaders).
- **2500+**: Grandmaster (Historical outliers).

## 🏟️ Application in MLB
In the PRO BALL PREDICTOR, the base Elo is adjusted for **Home Field Advantage (HFA)**, **Park Factors**, and **Travel Fatigue** before being passed to the Monte Carlo engine for run-scoring simulations.

---
*Reference: Arpad Elo, "The Rating of Chessplayers, Past and Present".*
*See Also: [Analytical Strategy](file:///c:/Users/clear/MLB/directives/analytical_strategy.md)*
