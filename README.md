Reliable gate, MILP limit margins, TATL fallback factor, MILP current in loadings, DC zero-reference fix

- Gate: exits non-zero when any stage fails; fixture zips compared by member content; README name fixed
- MILP: new factors milp_limit_factor_patl, _tatl and _scanned (default 1.0) applied to the limits in the MILP constraints and the N-X constraint filter only; the AC check and outputs keep the real limits
- TATL: new tatl_fallback_factor (default 1.0); a branch side without a TATL gets PATL x factor
- Outputs: current_milp_a and loading_milp_pct added to loadings_n0.csv and loadings_nx.csv
- DC mode: an N-X pair with a zero sensitivity reference and a load-flow current within the sensitivity guard floor is kept, with one summary warning
- With default settings, calculation results are unchanged
