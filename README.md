Read-only. Do not change any file, do not run the pipeline. Never print ids, names, EIC codes or values; counts only.
Load the CGM with pypowsybl the same way the pipeline does, and take network.get_operational_limits(all_attributes=True).
For the branches of the TSO whose EQ limits are labelled PATL with an acceptable duration:
1. How many branch sides have a permanent CURRENT limit (acceptable_duration -1), and how many have only temporary limits?
2. For the temporary-only sides: which acceptable_duration values occur (with counts), and which values occur in the "name" column (with counts)? Does the name say PATL?
3. Does any other TSO in the CGM have branch sides with no permanent CURRENT limit? Counts per TSO.
Answer as one short table.
