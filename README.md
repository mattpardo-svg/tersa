Do not run anything. Only write the script C:\temp\check_limits6.py and stop; I will run it myself. Write to the screen and to C:\temp\limits6.txt. Change nothing in the repo. Replace every id (mRID, rdf:ID, rdf:about) with T1, T2, ... before printing; names of limit types and attribute values may be printed.

1. Load the CGM as in cgmes_loader.load_cgm, with a report node: rn = pypowsybl.report.ReportNode(); pypowsybl.network.load(..., report_node=rn). Then take str(rn), and print the lines that contain "limit" or "Limit" (ids replaced), grouped with counts.
2. For F25, F24 and one file that works (F2): print each OperationalLimitType object in full: every property with its full namespace URI and value.
3. In F24, split the ACLineSegments into those with a limit in the network and those without. For each group, count by:
   - the OperationalLimitType their CurrentLimits reference (T1, T2, ...);
   - the ConductingEquipment type of the Terminal their OperationalLimitSet points to (ACLineSegment, Switch, Breaker, Disconnector, other);
   - and how many of the line's own terminals have no limit set at all.
4. For F25, count the ConductingEquipment type of all Terminals referenced by OperationalLimitSets.
One small table per point.
