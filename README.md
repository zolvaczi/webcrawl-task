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

## Requirement Clarification
### Q1: double check specification of `odds/probability`
`odds/probability` is for instance `15/2` for Spain on paddypower (see example at Methods)?

### Q2: Which column to take on betfair.com
Is it one specific column, or some sort of aggregation of all/some columns?

### Q3: start URL
"Preferably use text processing/analysis to navigate to correct match link from home URL instead of hardcoding the start URL"

### Q4: Team names as parameters
"Team names can also be used as parameter to locate correct odds elements on page"

## Methods
### find_by_html_class
Specify the exact HTML id/class name for each site.

Inspected HTML elements:

```
https://www.paddypower.com/football/uefa-euro-2020?tab=outrights
<p class="outright-item__runner-name">Spain</p>
<span class="btn-odds__label">15/2</span>
----
https://www.betfair.com/exchange/plus/en/football/uefa-euro-2020-betting-28814228
<h3 class="runner-name" data-ng-bind="::runnerName">Spain</h3>
Example ("Lay all" column):
<button class="lay mv-bet-button lay-button lay-selection-button" 
  data-bet-type="lay" data-ng-class="::{'is-sp': isSp}"
  type="lay" depth="0" price="9.4" size="£86" ...
  title="17/2">
	<!---->
	<!---->
	<div class="mv-bet-button-info" data-ng-if="::!isSp">
		<span class="bet-button-price">9.4</span>
		<span class="bet-button-size">£86</span>
	</div>
	<!---->
</button>
```

### find_class_by_sample
Specify some team names and current scores to find the appropriate class names.

## Further considerations
* more thorough testing (more websites) may show that certain country names appear in different forms on different websites (e.g. "United Kingdom", "UK", "Great Britain"), and as an extra feature, the code should be enhanced to handle these.

