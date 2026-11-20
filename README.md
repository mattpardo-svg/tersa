Change the NCP: shift T3's countertrade bid dates. A backup already exists; do not make another. Change nothing in the repo code. Print counts only, no ids or values.
1. Write a script outside the repo (C:\temp\shift_ct_dates.py) that, only in the file that holds T3's countertrade PowerBidSchedules, shifts every PowerBidScheduleTimePoint.atTime by +154 days (2024-12-03 becomes 2025-05-06; keep the clock time and the Z). Change nothing else in the file.
2. Apply the change in both places:
   - the NCP zip in input\ (rewrite that one file inside the zip, keep every other file as it is);
   - the same file in the _extracted_ncp\ folder.
3. Run the script, then report: time points shifted in the zip and in the extracted file, and how many T3 schedules now have a point at 2025-05-06 00:30Z in each.
4. Delete the script.
