# Neutral Bias Analysis Report

## 1. Basic Statistics

- Total votes: 1267
- Total voters: 179
- Total 1-point votes: 175 (13.81%)
- Total 0-point votes: -14

## 2. Theoretical Vote Distribution Analysis

### Quadratic Voting Cost Structure

| Vote Value | Cost (Credits) | Expected Ratio (Cost-Adjusted) | Expected Ratio (Uniform) |
|------------|----------------|--------------------------------|-------------------------|
| 1 | 1 | 64.94% | 11.11% |
| 2 | 4 | 16.24% | 11.11% |
| 3 | 9 | 7.22% | 11.11% |
| 4 | 16 | 4.06% | 11.11% |
| 5 | 25 | 2.60% | 11.11% |
| 6 | 36 | 1.80% | 11.11% |
| 7 | 49 | 1.33% | 11.11% |
| 8 | 64 | 1.01% | 11.11% |
| 9 | 81 | 0.80% | 11.11% |

### Distribution Test Results

#### Compared to Uniform Distribution
- Chi-square value: 348.5296
- p-value: 0.00000000
- Excess 1-point votes: 34.22 votes
- Excess 1-point percentage: 24.31%

#### Compared to Cost-Adjusted Distribution
- Chi-square value: 1133.4535
- p-value: 0.00000000
- Excess 1-point votes: -647.85 votes
- Excess 1-point percentage: -78.73%

**Result**: Vote values differ significantly even from the cost-adjusted distribution. Neutral bias likely exists beyond what can be explained by QV's cost structure.

## 3. 1-Point Vote Ratio by Project

| Project Name | Total Votes | 1-Point Votes | 1-Point % | Average 1-Point % | Deviation |
|--------------|---------|-------|---------|----------|----------|
| JINEN TRAVEL | 181 | 36 | 19.89% | 13.81% | +6.08% |
| Inatori Art Center Plan | 181 | 30 | 16.57% | 13.81% | +2.76% |
| Chiba Youth Center PRISM - Support for Teens and 20s | 181 | 25 | 13.81% | 13.81% | +0.00% |
| Para Travel Support Team | 181 | 23 | 12.71% | 13.81% | -1.10% |
| Politics to Festival #vote_for Project | 181 | 21 | 11.60% | 13.81% | -2.21% |
| Awaji Island Quest College | 181 | 21 | 11.60% | 13.81% | -2.21% |
| Bio Rice Field Project | 181 | 19 | 10.50% | 13.81% | -3.31% |

## 4. Voter Pattern Analysis

| 1-Point Use Pattern | Voter Count | Percentage |
|---------------|---------|------|
| Very Low 1s | 49 | 27.37% |
| Low 1s | 25 | 13.97% |
| Medium 1s | 16 | 8.94% |
| High 1s | 3 | 1.68% |
| Very High 1s | 0 | 0.00% |

## 5. Summary and Next Steps

The analysis suggests no evidence of neutral bias in the voting data. Specifically, 1-point votes (minimum vote value) are used -78.73% more than theoretically expected, even after accounting for QV's quadratic cost structure.

Based on these results, the following additional analyses are recommended:

1. Scenario simulation: Analyze budget allocation changes if a certain percentage of 1-point votes were converted to 0-point votes
2. Voter-specific analysis: Examine how different voting patterns impact neutral bias
3. UI design proposals: Develop voting interface improvements to mitigate bias
