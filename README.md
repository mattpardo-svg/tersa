
Read-only, no code changes. Run output/20250506T0030Z.
1. The log line "RD activated=276 generating unit(s) (197.6 MW redispatched)" disagrees with rd_results.csv and summary.csv (202.67 MW up). Find in the code what each number counts. Is the 5.07 MW gap units that are not connected, or something else? Does the AC verification apply 197.6 or 202.67 MW?
2. The run_profile steps add up to about 6,561 s, but run_time_s is 7,753 s. Which steps after "Apply and AC verification" are not profiled (N-X loadings, overload diagnosis, output writing, others)? Give file:line.
Answer in at most 10 lines.
