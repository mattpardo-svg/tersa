Read-only check. Do not change any file in the repo and do not run the pipeline. Never print ids, names, EIC codes or limit values; counts only (TSO short names are fine).

You may create one temporary Python script outside the repo (e.g. C:\temp\check_patl.py) and delete it at the end. Run it with .venv\Scripts\python.exe and write its output to C:\temp\patl_counts.txt, then read that file (the terminal may not show the output).

The script loads only the CGM in input\ with pypowsybl.network.load and the same parameters as cgmes_loader.load_cgm ("iidm.import.cgmes.source-for-iidm-id": "mRID", "iidm.import.cgmes.cgm-with-subnetworks": "false"). It does not load NCPs and does not run a load flow.

From network.get_operational_limits(), keep the CURRENT limits of lines, 2-winding transformers and dangling lines. Find each branch's TSO from its substation (network.get_substations(all_attributes=True), column TSO, via the voltage level).

Report per TSO:
1. Branch sides with a permanent CURRENT limit (acceptable_duration -1).
2. Branch sides with temporary CURRENT limits only.
3. Branches with no CURRENT limit at all.

For the temporary-only sides of all TSOs:
4. The acceptable_duration values that occur, with counts.
5. The values of the "name" column that occur, with counts. Does the name say PATL?

Answer as one short table, plus the two lists. Delete the temporary script and the output file at the end.
