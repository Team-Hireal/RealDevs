# Average Trend Calculation Verification

## Current Implementation

The average trend is calculated using **Least Squares Regression**, which is the standard method for calculating trendline slopes.

### Formula Used

```
slope = (n*Σ(xy) - Σ(x)*Σ(y)) / (n*Σ(x²) - (Σ(x))²)
```

Where:
- `n` = number of data points (days)
- `x` = day index (0, 1, 2, ..., n-1) where 0 is the oldest day
- `y` = daily weighted score for that day

### Why Least Squares (Not RMS)?

- **Least Squares Regression**: Used to calculate the slope of a best-fit line through data points. This is what we use for trend calculation.
- **Root Mean Square (RMS)**: Used to measure the error/deviation of data points from a trendline, not to calculate the trendline itself.

The current implementation is mathematically correct for calculating trendline slopes.

## Verification Tests

All tests pass, confirming the calculation works correctly:

1. ✅ **Upward trend test**: `[1, 2, 3, 4, 5]` → positive slope (~1.0)
2. ✅ **Downward trend test**: `[5, 4, 3, 2, 1]` → negative slope (~-1.0)
3. ✅ **Flat trend test**: `[3, 3, 3, 3, 3]` → slope ~0.0
4. ✅ **Realistic data test**: `[10, 12, 15, 18, 20]` → positive slope (~2.6)

## Potential Issues

If you're seeing a negative trend when the graph shows positive, possible causes:

1. **Data ordering**: Ensure `daily_scores` are ordered chronologically (oldest to newest)
2. **Missing data points**: Gaps in dates might affect the calculation
3. **Data aggregation**: Verify daily weighted scores are being calculated correctly

## Debugging

The calculation now includes debug logging. To see the calculation details, enable DEBUG logging:

```python
import logging
logging.getLogger('app.services.metrics_service').setLevel(logging.DEBUG)
```

This will log:
- Number of data points
- First and last scores
- Calculated slope

## Conclusion

The trend calculation formula is **mathematically correct** and uses the standard least squares regression method. If you're seeing incorrect results, the issue is likely in:
- Data preparation/aggregation
- Date sorting
- Missing data handling

The calculation itself is verified and working correctly.

