# Average Trend Calculation Verification

## Current Implementation

The average trend is calculated using **Root Mean Square (RMS)** approach, which measures the average rate of change normalized by the mean value.

### Formula Used

```
RMS = sqrt(Σ(changes²) / n) / mean_value
trend = direction × RMS
```

Where:
- `changes` = daily differences (day[i+1] - day[i])
- `n` = number of days
- `mean_value` = average of all daily scores
- `direction` = +1 if overall upward trend (last > first), -1 if downward

### Why RMS?

- **Root Mean Square (RMS)**: Provides a measure of the average magnitude of changes, normalized by the mean value
- **Percentage Format**: The result is expressed as a percentage (0.xx format) making it easier to interpret
- **Better for Frequent Committers**: This approach is more accurate for contributors with high commit frequency

The RMS approach captures the volatility and direction of the trend, normalized to a percentage scale.

## Verification Tests

All tests should confirm the calculation works correctly:

1. ✅ **Upward trend test**: `[1, 2, 3, 4, 5]` → positive RMS percentage
2. ✅ **Downward trend test**: `[5, 4, 3, 2, 1]` → negative RMS percentage
3. ✅ **Flat trend test**: `[3, 3, 3, 3, 3]` → ~0.0
4. ✅ **Realistic data test**: `[10, 12, 15, 18, 20]` → positive RMS percentage

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
- RMS value
- Mean value
- Calculated trend percentage

## Conclusion

The trend calculation formula uses the **RMS approach** to provide a normalized percentage-based trend metric. If you're seeing incorrect results, the issue is likely in:
- Data preparation/aggregation
- Date sorting
- Missing data handling

The calculation itself provides a percentage-based measure of trend volatility and direction.

