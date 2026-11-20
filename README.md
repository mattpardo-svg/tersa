Do not run anything. Only write the script C:\temp\check_patl2.py and stop; I will run it myself. It writes counts only (no ids, names or values) to the screen and to C:\temp\patl_counts2.txt. Change nothing in the repo.

The script loads only the CGM in input\ with pypowsybl.network.load and the parameters of cgmes_loader.load_cgm, and reads the Swissgrid EQ file inside the CGM zip as text.

1. From that EQ file, take the ids of all ACLineSegment and PowerTransformer objects (mRID, or rdf:ID / rdf:about without a leading underscore or "#").
2. For each id, look it up in the network (lines, 2-winding transformers, 3-winding transformers, dangling lines, tie lines; also try the id with and without a leading underscore). Count: found as which element type, or not found.
3. For the ids found, count by the limits in network.get_operational_limits() (for a tie line, the limits of its two dangling lines): permanent CURRENT limit, only APPARENT_POWER limits, only ACTIVE_POWER limits, no limit at all.
4. For all 2,851 network branches without a CURRENT limit: count them by element type, and by which other limit types they have (APPARENT_POWER, ACTIVE_POWER, none).
Print one small table per point.
