# 🧬 Sabermetrics & "Moneyball" Foundations

This directive codifies the principles of Sabermetrics and the "Moneyball" approach, serving as the analytical bedrock for the terminal's predictive engine.

## 🏁 Definition & Origins
- **Sabermetrics**: The empirical analysis of baseball, especially the development of advanced metrics. 
  - *Etymology*: Derived from **SABR** (Society for American Baseball Research, f. 1971).
  - *Pioneers*: Coined by **Bill James** (1980), who argued that baseball is defined by conditions (ballparks, players, ethics) rather than just rules.
- **Moneyball**: The use of metrics to identify "undervalued players" and sign them to "below market value" contracts. Popularized by **Billy Beane** and **Sandy Alderson** (Oakland Athletics).

## ⏳ Evolution of Analysis
### Early History
- **Henry Chadwick (1858)**: Developed the first box score, the progenitor of numerical tracking.
- **Earnshaw Cook (1964)**: Published *Percentage Baseball*, one of the first analytical takes, though initially dismissed by professionals.
- **Bill James (1977)**: *Baseball Abstracts* began the trend toward legitimacy in statistical science.

### Technical Pioneers
- **Davey Johnson (1970s)**: Used an IBM System/360 (FORTRAN) to run simulations for the Baltimore Orioles. Later used dBASE II for the NY Mets.
- **Craig R. Wright (1980s)**: The first front office employee in MLB history to hold the title "Sabermetrician" (Texas Rangers).
- **David Smith (1989)**: Founded **Retrosheet** to computerize every box score in MLB history.
- **Nate Silver (2003)**: Invented **PECOTA** (Player Empirical Comparison and Optimization Test Algorithm) for predictive career trajectories.

## 📊 Measurement Shift: Traditional vs. Advanced
### Batting: Moving Beyond BA
- **Batting Average (BA)**: Traditionally the primary measure, but flawed as it ignores walks and hits-by-pitch.
- **On-Base Percentage (OBP)**: Recognized as a superior predictor of run scoring (the goal of the game).
- **OPS (On-base plus slugging)**: A powerful method for predicting runs. **OPS+** further adjusts for eras and ballparks.
- **wOBA (Weighted On-Base Average)**: Refines OPS by assigning proper linear weights to each method of reaching base.

### Pitching: Isolating the Pitcher
- **ERA (Earned Run Average)**: The traditional standard, but fails to separate pitcher skill from fielder performance.
- **WHIP (Walks + Hits per IP)**: A better indicator of base-runner management.
- **DIPS (Defense Independent Pitching Statistics)**: Developed by **Voros McCracken** (1999). Proves pitchers have little control over hits allowed on balls in play (BABIP).
- **FIP (Fielding Independent Pitching)**: Focuses only on events the pitcher controls (HR, BB, K).

## 💎 High-Dimensional Metrics
- **VORP (Value Over Replacement Player)**: Measures contribution relative to a minimum-level roster player.
- **WAR (Wins Above Replacement)**: A cumulative metric determining additional wins provided relative to a replacement-level player at that position.
- **Statcast (2015+)**: Uses **PITCHf/x** and radar technology to record exit velocity, launch angles, and pitch break characteristics.

## 🏟️ Applications
- **In-Game Strategy**: Determining when to steal, when to bring in a closer, and selecting optimal batter/pitcher match-ups ("playing the percentages").
- **Valuation**: Contract negotiations, arbitration, and scouting (Minor-League Equivalency).

---
*Reference: Michael Lewis, "Moneyball: The Art of Winning an Unfair Game" (2003).*
*See Also: [Full Statistics Glossary](file:///c:/Users/clear/MLB/directives/mlb_statistics_glossary.md)*
