Do not run anything. Only write the script C:\temp\check_limits7.py and stop; I will run it myself. Counts only (no ids, no limit values), to the screen and to C:\temp\limits7.txt. Change nothing in the repo.
Load the CGM as in cgmes_loader.load_cgm. Read the ids in C:\temp\nolimit_ids.txt.
1. Call network.get_operational_limits(all_attributes=True, show_inactive_sets=True). For the lines in nolimit_ids.txt, count branch sides that now have a CURRENT limit with acceptable_duration -1.
2. For those sides: the number of limit groups per side (with counts); the group names that occur (the group_name column), with counts.
3. Per side with several groups: do the PATL values differ between groups? Count sides where they are equal and where they differ; for the differing ones, give the ratio max/min as a range (min ratio, max ratio).
4. network.get_branches(all_attributes=True): for these lines, count the values of selected_limits_group_1 and selected_limits_group_2 (empty or not).
