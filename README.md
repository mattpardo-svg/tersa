Read-only, counts only, no ids or values. Do not change the repo. For the 3,004 countertrade PowerBidSchedules in the NCP:
1. The format of PowerBidScheduleTimePoint.atTime: how many end in "Z", how many carry an offset (+01:00, +02:00, other), how many have no zone.
2. After converting every atTime to UTC: how many schedules have a point exactly at the run date and time (2025-05-06 00:30Z)?
3. The spacing between consecutive points (15 min, 30 min, 60 min, other), with counts, and the clock minutes used (:00, :15, :30, :45), with counts, both in UTC.
4. Per TSO short name (or T1, T2 ...): schedules, and schedules with a point at the run time before and after the UTC conversion.
One small table per point.
