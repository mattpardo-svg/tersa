Do not run anything. Only write the script C:\temp\check_limits5.py and stop; I will run it myself. Counts only, to the screen and to C:\temp\limits5.txt. Change nothing in the repo.
For each EQ file in the CGM zip (F1, F2, ... in the same archive order as before):
1. CurrentLimit objects, and how many of them have each property: CurrentLimit.normalValue, CurrentLimit.value, OperationalLimit.OperationalLimitSet, OperationalLimit.OperationalLimitType, and any other property name (list them with counts).
2. OperationalLimitSet objects, and how many have each property (OperationalLimitSet.Terminal, OperationalLimitSet.Equipment, others).
3. The XML namespace prefix used for these properties (cim / entsoe / other), with counts.
4. The CGMES version in the file header (the Model.profile URIs), with counts.
One table per point, one row per file. Show F24 and F25 first, then the rest.
