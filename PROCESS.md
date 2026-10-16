# How I plan the next work (Scrum-style)

This is the plan for the next sprints of **Analysis-of-Rice-straw-Boiler**. It is a planned way of working for a one-person project, not a record of past team work.

## Working agreement
- Sprint: one week. Sprint goal: one backlog item finished, with its numbers in `reports/` and the README.
- Planning on Monday (pick items), review on Friday (open the project page, check the numbers), a short retrospective note in the commit log.
- Board: one GitHub issue per backlog item, columns To do, In progress, Done (GitHub Projects).
- Branches: `main` stays working; each item gets its own branch and a pull request.

## Definition of done
1. The script runs in a fresh virtual environment from `requirements.txt`.
2. Every number in the README and on the page matches `reports/`.
3. The project page opens without console errors and works on a phone.
4. No secrets or personal data in the files or history.
5. Limits are stated next to the result.

## Product backlog
| # | User story | Acceptance |
|---|---|---|
| 1 | As an engineer, I want a loss term for unburnt fuel and CO, so that the model has a real optimum above the lowest air setting. | Efficiency curve with a maximum inside the range; sources for the loss terms. |
| 2 | As an engineer, I want measured plant data, so that the model is checked against a real boiler. | One measured series compared; deviations shown. |
| 3 | As a reader, I want uncertainty from the input constants, so that the efficiency has a range. | Monte Carlo over constants, range on the chart. |
