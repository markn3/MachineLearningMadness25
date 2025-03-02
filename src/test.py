# Step 5: Compute the rolling/dynamic rating per team (average NetRtg from all previous games)
def compute_rolling_rating(group):
    roll_net = []
    roll_off = []
    roll_def = []
    cumulative_net = 0.0
    cumulative_off = 0.0
    cumulative_def = 0.0
    count = 0
    for net in group['NetRtg']:
        if count == 0:
            dynamic_ratings.append(np.nan)  # No previous game exists
        else:
            dynamic_ratings.append(cumulative_sum / count)
        cumulative_sum += net
        count += 1
    group = group.copy()
    group['DynamicRating'] = dynamic_ratings
    return group

def compute_rolling_ratings(group):
    roll_net = []
    roll_off = []
    roll_def = []
    cumulative_net = 0.0
    cumulative_off = 0.0
    cumulative_def = 0.0
    count = 0
    # Iterate over the rows in this group (which is already sorted by DayNum)
    for net, off, defe in zip(group['NetRtg'], group['OffRtg'], group['DefRtg']):
        if count == 0:
            # For the first game, there's no previous game, so assign NaN
            roll_net.append(np.nan)
            roll_off.append(np.nan)
            roll_def.append(np.nan)
        else:
            roll_net.append(cumulative_net / count)
            roll_off.append(cumulative_off / count)
            roll_def.append(cumulative_def / count)
        # Update cumulative sums and game count
        cumulative_net += net
        cumulative_off += off
        cumulative_def += defe
        count += 1
    group = group.copy()
    group['roll_net'] = roll_net
    group['roll_off'] = roll_off
    group['roll_def'] = roll_def
    return group
