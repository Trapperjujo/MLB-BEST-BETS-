# 📚 MLB Statistics Glossary

This directive serves as the institutional memory for MLB statistical definitions, categorized by game aspect. Use this as the ground truth for data interpretation in predictive models.

## 🏏 Batting Statistics
*For historical context and development of these metrics, see [mlb_statistics_context.md](file:///c:/Users/clear/MLB/directives/mlb_statistics_context.md)*

- **1B – Single**: hits on which the batter reaches first base safely without the contribution of a fielding error
- **2B – Double**: hits on which the batter reaches second base safely without the contribution of a fielding error
- **3B – Triple**: hits on which the batter reaches third base safely without the contribution of a fielding error
- **AB – At bat**: plate appearances, not including bases on balls, being hit by pitch, sacrifices, interference, or obstruction
- **AB/HR – At bats per home run**: at bats divided by home runs
- **BA – Batting average (also abbreviated AVG)**: hits divided by at bats (H/AB)
- **BB – Base on balls (also called a "walk")**: hitter not swinging at four pitches called out of the strike zone and awarded first base.
- **BABIP – Batting average on balls in play**: frequency at which a batter reaches a base after putting the ball in the field of play. Also a pitching category.
- **BB/K – Walk-to-strikeout ratio**: number of bases on balls divided by number of strikeouts
- **BsR – Base runs**: Another run estimator, like runs created
- **EQA – Equivalent average**: a player's batting average absent park and league factors
- **FC – Fielder's choice**: times reaching base safely because a fielder chose to try for an out on another runner
- **GO/AO – Ground ball fly ball ratio**: number of ground ball outs divided by number of fly ball outs
- **GDP or GIDP – Ground into double play**: number of ground balls hit that became double plays
- **GPA – Gross production average**: 1.8 times on-base percentage plus slugging percentage, divided by four
- **GS – Grand slam**: a home run with the bases loaded, resulting in four runs scoring, and four RBIs credited to the batter
- **H – Hit**: reaching base because of a batted, fair ball without error by the defense
- **HBP – Hit by pitch**: times touched by a pitch and awarded first base as a result
- **HR – Home runs**: hits on which the batter successfully touched all four bases, without the contribution of a fielding error
- **HR/H – Home runs per hit**: home runs divided by total hits
- **ITPHR – Inside-the-park home run**: hits on which the batter successfully touched all four bases, without the contribution of a fielding error or the ball going outside the ball park.
- **IBB – Intentional base on balls**: times awarded first base on balls deliberately thrown by the pitcher. Also known as IW (intentional walk).
- **ISO – Isolated power**: a hitter's ability to hit for extra bases, calculated by subtracting batting average from slugging percentage
- **K – Strike out (also abbreviated SO)**: number of times that a third strike is taken or swung at and missed, or bunted foul.
- **LOB – Left on base**: number of runners neither out nor scored at the end of an inning
- **OBP – On-base percentage**: times reached base (H + BB + HBP) divided by at bats plus walks plus hit by pitch plus sacrifice flies (AB + BB + HBP + SF)
- **OPS – On-base plus slugging**: on-base percentage plus slugging average
- **PA – Plate appearance**: number of completed batting appearances
- **PA/SO – Plate appearances per strikeout**: number of times a batter strikes out to their plate appearance
- **R – Runs scored**: number of times a player crosses home plate
- **RC – Runs created**: an attempt to measure how many runs a player has contributed to their team
- **RP – Runs produced**: an attempt to measure how many runs a player has contributed
- **RBI – Run batted in**: number of runners who score due to a batter's action, except when the batter grounded into a double play or reached on an error
- **RISP – Runner in scoring position**: batting average with runners at second or third base
- **SF – Sacrifice fly**: fly balls hit to the outfield which, although caught for an out, allow a baserunner to advance
- **SH – Sacrifice hit**: number of sacrifice bunts which allow runners to advance on the basepaths
- **SLG – Slugging percentage**: total bases achieved on hits divided by at-bats (TB/AB)
- **TA – Total average**: [(TB + BB + HBP + SB – CS)/(AB – H + CS + GIDP)]
- **TB – Total bases**: [1B + (2 × 2B) + (3 × 3B) + (4 × HR)]
- **TOB – Times on base**: (H + BB + HBP)
- **XBH – Extra base hits**: (2B + 3B + HR)

## 🏃 Baserunning Statistics
- **SB – Stolen base**: number of bases advanced by the runner while the ball is in possession of the defense
- **CS – Caught stealing**: times tagged out while attempting to steal a base
- **SBA or ATT – Stolen base attempts**: total number of times the player has attempted to steal a base (SB+CS)
- **SB% – Stolen base percentage**: (SB) / (SBA)
- **DI – Defensive Indifference**: when the catcher does not attempt to throw out a runner (scored as fielder's choice)
- **R – Runs scored**: times reached home plate legally and safely
- **UBR – Ultimate base running**: metric for the impact of a player's baserunning skill using linear weights

## 投手 Pitching Statistics
- **BB – Base on balls (also called a "walk")**: times pitching four balls, allowing first base
- **BB/9 – Bases on balls per 9 innings pitched**: (BB * 9) / IP
- **BF – Total batters faced**: opponent team's total plate appearances
- **BK – Balk**: illegal pitching action resulting in baserunners advancing
- **BS – Blown save**: entering in a save situation and losing the lead
- **CERA – Component ERA**: estimate of ERA based on individual components (K, H, 2B, 3B, HR, BB, HBP)
- **CG – Complete game**: games where player was the only pitcher for their team
- **DICE – Defense-Independent Component ERA**: estimate based on defense-independent components
- **ER – Earned run**: runs that did not occur due to errors or passed balls
- **ERA – Earned run average**: (ER * 9) / IP
- **ERA+ – Adjusted ERA+**: ERA adjusted for ballpark and league average
- **FIP – Fielding independent pitching**: focuses on events within pitcher's control (HR, BB, K)
- **xFIP**: substitutes pitcher's HR% with league average
- **G – Games (appearances)**: number of times a pitcher pitches in a season
- **GF – Games finished**: number of games pitched where player was the final pitcher for their team
- **GIDP – Double plays induced**: number of double play groundouts induced
- **GIDPO – Double play opportunities**: groundout induced double play opportunities
- **GIR – Games in relief**: games as a non-starting pitcher
- **GO/AO or G/F**: ground balls allowed / fly balls allowed
- **GS – Starts**: number of games pitched as the first pitcher
- **H (or HA) – Hits allowed**: total hits allowed
- **H/9 (or HA/9)**: hits allowed per 9 innings (H * 9) / IP
- **HB – Hit batsman**: times hitting a batter with a pitch
- **HLD (or H) – Hold**: entering in save situation, recording out, not surrendering lead, not finishing game
- **HR (or HRA) – Home runs allowed**: total home runs allowed
- **HR/9 (or HRA/9)**: (HR * 9) / IP
- **IBB – Intentional base on balls allowed**
- **IP – Innings pitched**: outs / 3
- **IP/GS – Average innings per game started**
- **IR – Inherited runners**: runners on base when pitcher enters
- **IRA – Inherited runs allowed**: inherited runners allowed to score
- **K (or SO) – Strikeout**: batters receiving strike three
- **K/9 (or SO/9)**: (K * 9) / IP
- **K/BB (or SO/BB)**: K / BB ratio
- **L – Loss**: pitching while opposing team takes the lead and wins
- **LOB% – Left-on-base percentage**: percentage of baserunners a pitcher does not allow to score
- **OBA (or AVG) – Opponents’ batting average**: H / AB faced
- **PC-ST – Pitch Count - Strikes Thrown**: total pitches and number of strikes within those pitches
- **PIT (or NP) – Pitches thrown (Pitch count)**
- **PFR – Power finesse ratio**: (K + BB) / IP
- **pNERD – Pitcher's NERD**: expected aesthetic pleasure of watching a pitcher
- **QOP – Quality of pitch**: combines speed, location, and movement into a numeric value
- **QS – Quality start**: 6+ IP and 3 or fewer ER
- **RA – Run average**: (R * 9) / IP
- **SHO – Shutout**: complete game with no runs allowed
- **SIERA – Skill-Interactive Earned Run Average**: advanced stat measuring pitching skill
- **SV – Save**: finishing a game under specific lead conditions
- **SVO – Save opportunity**: entering in a save-eligible situation
- **W – Win**: pitching while team takes lead and wins (minimum 5 IP for starters)
- **W + S – Wins in relief + saves**
- **whiff rate**: swings and misses / total swings
- **WHIP – Walks and hits per inning pitched**: (W + H) / IP
- **WP – Wild pitches**: pitches too wild for catcher to field, allowing advancement

## 🛡️ Fielding Statistics
- **A – Assists**: outs recorded where fielder touched ball but didn't record putout
- **CI – Catcher's Interference**: catcher makes contact with bat
- **DP – Double plays**: participation in a double play
- **E – Errors**: failure to make a routine play
- **FP – Fielding percentage**: (TC - E) / TC
- **INN – Innings**: innings at a specific position
- **PB – Passed ball**: dropped ball by catcher allowing advancement
- **PO – Putout**: tagging or forcing a runner for an out
- **RF – Range factor**: 9 * (PO + A) / INN
- **TC – Total chances**: A + PO + E
- **TP – Triple play**: participation in a triple play
- **UZR – Ultimate zone rating**: ability to defend an assigned zone vs average

## 💎 Overall Player Value
- **VORP – Value over replacement player**: value compared to a replacement-level player
- **Win shares**: metric for overall contribution to team wins
- **WAR – Wins above replacement**: wins contributed over a replacement-level player
- **PWA – Player Win Average**: increase/decrease in team win probability per game
- **PGP – Player Game Percentage**: sum of win probability changes for all plays participated in

## 🏟️ General Statistics
- **G – Games played**: total games appeared in
- **GS – Games started**: total games started
- **GB – Games behind**: games behind the division leader
- **Pythagorean expectation**: expected Win% based on runs scored and allowed
