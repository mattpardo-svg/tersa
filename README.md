Updated task order

W1: reliable gate. The gate fails when any stage fails. Zip fixtures are compared by content instead of raw bytes, and docs/readme.md becomes README.md. This clears the 6 failing tests and makes the gate trustworthy for every later step.
Tests (Sonar S5863, Ruff F811/F821). Restore the hidden HVDC test, delete the dead helper with the undefined name, and make the 4 self-comparisons explicit. This makes sure the test suite really tests what it claims.
Static cleanup (Ruff F401/F811/F841, Sonar S1764/S1244/S5332). The coder works from the architects’ report files: unused imports, the duplicate imports in helpers.py, and explicit NaN checks. The exact-zero checks, Pyomo constraints and namespace URIs are listed as false positives, and no results change.
W2: correctness and failure handling (CC3, CC4, 6.8.3 [Q]).
Penalties must be finite, and CSV rows must match their columns.
The two AC-loop gaps get fixed (voltage restore, stale N-X results), and the source-of-truth answer is recorded in DECISIONS.md.
The confirmed resource and error fixes go here too, plus the missing fallback to the default config found in the probe.
W4: module boundaries. Move the private milp_builder helpers that export code uses into a public module. This removes the hidden coupling the review flagged.
W3: run isolation (CC1, CC2, Sonar S8786). Each run gets its own folder and a “complete” marker, and the GUI shows only finished results from its own run. The GUI import of run_pipeline and the two slow regexes are fixed in the same step.
W5: dependencies. Upgrade pillow to 13.0.0 if streamlit allows it, otherwise record it as blocked. The numpy 2.5.3 bump goes into the change summary.
W7: open-item register and handover (W6, D1). Record what stays open:
CI not available (W6)
import-time config and logging (D1)
packaging and sys.path inserts
Legal review of MPL-2.0
ownership and service shape

Then write the reviewer instructions and the change summary for submission.

Each step ends with tests and the gate passing, and a summary with the base commit and the item IDs.
