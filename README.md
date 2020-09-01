# webcrawl-task

Task is to write a BOT, which can extract odds/probability for all the teams in Euro 2020 Win Outright market from links give below and generate a real-time matrix from it. Code should either print matrix to screen or save it in file at given interval (by default every 5 minutes). Preferably use text processing/analysis to navigate to correct match link from home URL instead of hardcoding the start URL. Team names can also be used as parameter to locate correct odds elements on page.

For example, the matrix should have following format.

||	Site1	|Site2	|Site3|
|---|---|---|---|
|Team1||||
|Team2||||
|Team3||||

List of web pages to extract odds from are as follows:
* https://www.paddypower.com/footbmeall/uefa-euro-2020?tab=outrights
* https://www.betfair.com/exchange/plus/en/football/uefa-euro-2020-betting-28814228

# Quick Analysis

## Methods
* find_by_html_class
* find_by_team_name_sample

## Further considerations
* more thorough testing (more websites) may show that certain country names appear in different forms on different websites (e.g. "United Kingdom", "UK", "Great Britain"), and as an extra feature, the code should be enhanced to handle these.

