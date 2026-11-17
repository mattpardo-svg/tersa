Task: read-only probe. Do not change, create or delete any file, and do not commit. Do not run the full test suite.

DATA RULE: no real data exists here. Use only mock or obviously synthetic values. Never write names or codes of real TSOs, zones, units or substations, or real-looking file names, in your report.

No plan or item numbers, and no personal, tool or model names in your report.

Line numbers below refer to commit 2da8400107ac568cf709cc2eaf5a40d2b4659010. If the code has moved, find the same statement by its content.

1. Repo state: report the current commit, whether 2da8400107ac568cf709cc2eaf5a40d2b4659010 is in the history, and how many commits came after it. Use the repo's own commit tool if git is not available.

2. Config defaults: which YAML file does the code actually load its defaults from, rao_config.yaml or rao_config.default.yaml? Name the function and line. Say what the other file is used for, or whether it is unused.

3. pillow: run .venv\Scripts\python.exe -m pip show pillow and report the version and the "Required-by" line. Say whether src/ imports PIL directly anywhere.

4. AC convergence loop (src/rao/milp/ac_convergence_loop.py): explain in at most 8 lines what happens after an iteration is reverted. Which one is the source of truth for the next iteration: the OperatingPointState or the network object that was changed? Can the two disagree after a revert? Point to the lines.

5. Float equality: for each line below, quote the statement and classify it as A (exact zero or exact value set by the code itself, intentional), B (NaN check written as x != x or x == x), C (compares computed floats, may need a tolerance), or D (other, explain in one line).
   milp/milp_builder.py: 779, 940, 954, 1048, 1206, 1377, 1740, 2111, 2133, 2151, 2164, 2169, 2794
   milp/nx_constraint_filter.py: 28
   milp/post_ra_congestion_check.py: 155
   post_milp/nx_results_export.py: 89, 107, 113
   pre_milp/cgmes_loader.py: 322, 466
   pre_milp/ct_weights.py: 68
   pre_milp/dc_conversion.py: 131
   pre_milp/hvdc_units.py: 149
   pre_milp/n0_sensitivity.py: 63, 516, 517
   pre_milp/nx_sensitivity.py: 281, 487, 488, 891
   pre_milp/sensitivity_checks.py: 67
   pre_milp/sensitivity_table.py: 124
   (all under src/rao/)

6. Tests:
   a. tests/test_rao_hvdc_parser.py: test_restrictive_group_found_with_the_depending_predicate is defined at lines 216 and 223. Are the two bodies different? Which one runs today?
   b. tests/test_rao_n0_results_export.py line 422 uses extract_results_generating_units, which is undefined. Does that line ever run? Is there a function with a similar name in src/?
   c. Assertions that compare a value with itself: tests/test_rao_cgmes_loader.py:478, tests/test_rao_dc_pass.py:98, tests/test_rao_n0_sensitivity.py:816, tests/test_rao_ncp_legacy_equivalence.py:334. Quote each and say what it was probably meant to compare.

7. Ruff: if ruff is installed, run it with its default rules on src/ and tests/ and report the count per rule code. If it is not installed, say so and do not install it.

Report: one short section per step, no code changes proposed beyond one line per item.
