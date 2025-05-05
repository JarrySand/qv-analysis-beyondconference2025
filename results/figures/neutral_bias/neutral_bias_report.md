# Neutral Bias Analysis Report

## 1. Basic Statistics

- Total votes: 931
- Total voters: 124
- Total 1-point votes: 138 (14.82%)
- Total 0-point votes: -63

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
- Chi-square value: 291.7487
- p-value: 0.00000000
- Excess 1-point votes: 34.56 votes
- Excess 1-point percentage: 33.40%

#### Compared to Cost-Adjusted Distribution
- Chi-square value: 988.6016
- p-value: 0.00000000
- Excess 1-point votes: -466.64 votes
- Excess 1-point percentage: -77.18%

**Result**: Vote values differ significantly even from the cost-adjusted distribution. Neutral bias likely exists beyond what can be explained by QV's cost structure.

## 3. 1-Point Vote Ratio by Project

| Project Name | Total Votes | 1-Point Votes | 1-Point % | Average 1-Point % | Deviation |
|--------------|---------|-------|---------|----------|----------|
| JINEN TRAVEL | 133 | 25 | 18.80% | 14.82% | +3.97% |
| Inatori Art Center Plan | 133 | 24 | 18.05% | 14.82% | +3.22% |
| Politics to Festival #vote_for Project | 133 | 21 | 15.79% | 14.82% | +0.97% |
| Para Travel Support Team | 133 | 20 | 15.04% | 14.82% | +0.21% |
| Chiba Youth Center PRISM - Support for Teens and 20s | 133 | 17 | 12.78% | 14.82% | -2.04% |
| Awaji Island Quest College | 133 | 16 | 12.03% | 14.82% | -2.79% |
| Bio Rice Field Project | 133 | 15 | 11.28% | 14.82% | -3.54% |

## 4. Voter Pattern Analysis

| 1-Point Use Pattern | Voter Count | Percentage |
|---------------|---------|------|
| Very Low 1s | 38 | 30.65% |
| Low 1s | 17 | 13.71% |
| Medium 1s | 12 | 9.68% |
| High 1s | 2 | 1.61% |
| Very High 1s | 0 | 0.00% |

## 5. Summary and Next Steps

The analysis suggests no evidence of neutral bias in the voting data. Specifically, 1-point votes (minimum vote value) are used -77.18% more than theoretically expected, even after accounting for QV's quadratic cost structure.

Based on these results, the following additional analyses are recommended:

1. Scenario simulation: Analyze budget allocation changes if a certain percentage of 1-point votes were converted to 0-point votes
2. Voter-specific analysis: Examine how different voting patterns impact neutral bias
3. UI design proposals: Develop voting interface improvements to mitigate bias
