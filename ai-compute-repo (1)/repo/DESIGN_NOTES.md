# Design notes: a chart and an interaction I owned

Draft written with Claude's help. Edit it so it states what you actually weighed.

## Chart: training compute over time (main scatter)
- **Visual task:** show how fast the compute used to train notable models has grown, let a reader compare domains, and read a doubling time off the trend.
- **Form chosen:** a scatter of publication date (x) against training compute in FLOP (y, log scale), one dot per model, coloured by domain, with a dashed least-squares line and the five largest models labelled.
- **Alternative rejected:** the same scatter on a linear y-axis.
- **Specific reason:** in the default selection (400 models, 2012 onward, four domains) compute runs from 7.6e13 to 9.4e26 FLOP, about 13 orders of magnitude. On a linear axis, 73% of models fall below one thousandth of the largest, so they would sit within the bottom 0.1% of the chart and be indistinguishable. Exponential growth would also look like a sudden jump, not a straight line whose slope gives the doubling time.

## Chart: models published per year
- **Visual task:** show how many notable models appear each year, so a reader can judge how noisy the yearly medians and fits are.
- **Form chosen:** a single-colour bar chart of the yearly total with the count printed above each bar.
- **Alternative rejected:** a stacked bar chart split by domain.
- **Specific reason:** with the four default domains there are 44 year-and-domain segments, 22 of them with five models or fewer and 9 with two or fewer. Those segments are too small to carry a printed value, which would fail the rule that every value is readable without hovering. The domain split is already shown by colour in the main scatter.

## Interaction: year slider and domain selector
- **Visual task:** let a reader test whether the compute trend holds for a subset instead of one average over very different eras.
- **Form chosen:** a sidebar year-range slider and a domain multi-select (up to seven), which update every chart, tile and the stated baseline together.
- **Alternative rejected:** a separate "compare two periods" panel.
- **Specific reason:** it would duplicate the charts, add a second set of numbers to explain, and lengthen a page that must scroll only vertically at 1366x768. One shared filter keeps every number on screen on the same baseline.
