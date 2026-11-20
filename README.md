Read-only, counts only, no ids or names. Do not change anything.
For MAVIR's 161 distinct equipment ids referenced by its assessed elements and contingencies:
1. How many of them appear anywhere in the CGM zip (any file, any profile), and as which class (ACLineSegment, Line, Terminal, PowerTransformer, Switch, OperationalLimitSet, other)?
2. Which property in the NCP holds the reference (e.g. AssessedElement.ConductingEquipment, .Line, ContingencyElement.Equipment), with counts.
3. If the NCP gives names for these objects (IdentifiedObject.name or in the AE/contingency name): how many of those names match the name of a MAVIR ACLineSegment, Line or PowerTransformer in the CGM (exact, and after ignoring case and spaces)?
One small table per point.
