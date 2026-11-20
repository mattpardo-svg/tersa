Do not run anything. Only write the script C:\temp\check_limits3.py and stop; I will run it myself. Counts and message texts only (no ids, names or limit values), to the screen and to C:\temp\limits3.txt. Change nothing in the repo.

1. Load the CGM in input\ with pypowsybl.network.load, the same parameters as cgmes_loader.load_cgm, and a report node (pypowsybl.report.ReportNode, passed as report_node). From the report, list every message that mentions a limit (OperationalLimit, CurrentLimit, limit type, PATL, TATL, acceptableDuration), grouped by message text with the ids removed, with counts.
2. Read the Swissgrid EQ file inside the CGM zip as text and count:
   - OperationalLimitSet, CurrentLimit, ApparentPowerLimit, ActivePowerLimit, OperationalLimitType objects;
   - CurrentLimits whose OperationalLimitType reference points to a type defined in the same file, and those whose type is not found;
   - the values of OperationalLimitType.kind (or limitType), isInfiniteDuration and acceptableDuration, with counts;
   - OperationalLimitSets that reference a Terminal, and those that reference an Equipment; and how many of those Terminals / Equipment are defined in the file.
3. Repeat point 2 for the EQ file of the TSO with the most lines without a limit (find it by counting, per EQ file, the ACLineSegments that have no limit in the network).
Print one small table per point.
