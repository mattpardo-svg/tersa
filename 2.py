"""tests/test_rao_cgmes_loader.py - unit tests for cgmes_loader.py.
"""

import sys
import types
import pandas as pd
import pytest
import logging

from pre_milp.cgmes_loader import (
    build_lf_initial,
    build_cgm_static_patl,
    build_pst_degrees_per_tap,
    run_initial_loadflow,
)
from pathlib import Path

# ---------------------------------------------------------------------------
# run_initial_loadflow — use_reactive_limits threading
# ---------------------------------------------------------------------------

class DummyLoadflowResultForReactiveLimits:
    def __init__(self, status_name="CONVERGED"):
        import types
        self.status = types.SimpleNamespace(name=status_name)


class SpyParameters:
    """Spy: records the kwargs it was constructed with, to check that use_reactive_limits
    reaches pp.loadflow.Parameters()."""
    last_kwargs = None

    def __init__(self, **kwargs):
        SpyParameters.last_kwargs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestRunInitialLoadflowUseReactiveLimits:
    def _install_fake_pypowsybl(self, monkeypatch):
        import types
        fake_module = types.ModuleType("pypowsybl")

        class loadflow:
            Parameters = SpyParameters

            @staticmethod
            def run_ac(network, parameters=None):
                return [DummyLoadflowResultForReactiveLimits()]

        fake_module.loadflow = loadflow
        monkeypatch.setitem(sys.modules, "pypowsybl", fake_module)
        SpyParameters.last_kwargs = None

    def test_default_reaches_parameters_construction_as_false(self, monkeypatch):
        self._install_fake_pypowsybl(monkeypatch)
        run_initial_loadflow(network=object())
        assert SpyParameters.last_kwargs == {"use_reactive_limits": False}

    def test_explicit_true_reaches_parameters_construction(self, monkeypatch):
        self._install_fake_pypowsybl(monkeypatch)
        run_initial_loadflow(network=object(), use_reactive_limits=True)
        assert SpyParameters.last_kwargs == {"use_reactive_limits": True}

    def test_explicit_false_reaches_parameters_construction(self, monkeypatch):
        self._install_fake_pypowsybl(monkeypatch)
        run_initial_loadflow(network=object(), use_reactive_limits=False)
        assert SpyParameters.last_kwargs == {"use_reactive_limits": False}


# ---------------------------------------------------------------------------
# build_lf_initial
# ---------------------------------------------------------------------------

class DummyLinesResult:
    def __init__(self, data: dict):
        self.index = list(data.keys())
        self._data = data

    @property
    def loc(self):
        return self._data


class DummyNetworkForLfInitial:
    def __init__(self, lines_data=None, trafo_data=None):
        self._lines_data = lines_data or {}
        self._trafo_data = trafo_data or {}

    def get_lines_results(self):
        return DummyLinesResult(self._lines_data)

    def get_2_windings_transformers_results(self):
        return DummyLinesResult(self._trafo_data)


class TestBuildLfInitial:
    def test_returns_both_sides_not_collapsed(self):
        """build_lf_initial returns BOTH i1 and i2 per branch, not max(i1, i2): limits are
        side-specific."""
        network = DummyNetworkForLfInitial(
            lines_data={"line1": {"i1": 100.0, "i2": 250.0}},
        )
        result = build_lf_initial(network)
        assert result["line1"] == {1: 100.0, 2: 250.0}
        # Explicitly NOT collapsed to max(100.0, 250.0) = 250.0
        assert result["line1"] != 250.0

    def test_missing_columns_give_nan_not_zero(self):
        network = DummyNetworkForLfInitial(lines_data={"line1": {}})
        result = build_lf_initial(network)
        assert all(value != value for value in result["line1"].values())

    def test_combines_lines_and_transformers(self):
        network = DummyNetworkForLfInitial(
            lines_data={"line1": {"i1": 100.0, "i2": 100.0}},
            trafo_data={"trafo1": {"i1": 50.0, "i2": 90.0}},
        )
        result = build_lf_initial(network)
        assert "line1" in result
        assert "trafo1" in result
        assert result["trafo1"] == {1: 50.0, 2: 90.0}


# ---------------------------------------------------------------------------
# build_cgm_static_patl
# ---------------------------------------------------------------------------

class DummyNetworkForStaticPatl:
    def __init__(self, df: pd.DataFrame):
        self._df = df

    def get_operational_limits(self):
        return self._df


def _make_operational_limits_df(rows: list[dict]) -> pd.DataFrame:
    """rows: list of dicts with keys element_id, side, type,
    acceptable_duration, group_name, element_type, name, value."""
    df = pd.DataFrame(rows)
    return df.set_index(["element_id", "side", "type", "acceptable_duration", "group_name"])


class TestBuildCgmStaticPatl:
    def test_returns_per_side_not_collapsed(self):
        """build_cgm_static_patl returns BOTH sides per branch, not min(side ONE, side TWO)."""
        df = _make_operational_limits_df([
            dict(element_id="b1", side="ONE", type="CURRENT", acceptable_duration=-1,
                 group_name="g1", element_type="LINE", name="permanent_limit", value=1000.0),
            dict(element_id="b1", side="TWO", type="CURRENT", acceptable_duration=-1,
                 group_name="g2", element_type="LINE", name="permanent_limit", value=1530.0),
        ])
        network = DummyNetworkForStaticPatl(df)
        result = build_cgm_static_patl(network)
        assert result["b1"] == {1: 1000.0, 2: 1530.0}
        # Explicitly NOT collapsed to min(1000.0, 1530.0) = 1000.0 only
        assert 2 in result["b1"]

    def test_excludes_tatl_entries(self):
        """TATL (finite acceptable_duration, e.g. 600s) must be excluded —
        only the permanent (acceptable_duration == -1) limit is PATL."""
        df = _make_operational_limits_df([
            dict(element_id="b1", side="ONE", type="CURRENT", acceptable_duration=-1,
                 group_name="g1", element_type="LINE", name="permanent_limit", value=1000.0),
            dict(element_id="b1", side="ONE", type="CURRENT", acceptable_duration=600,
                 group_name="g2", element_type="LINE", name="tatl_600", value=1500.0),
        ])
        network = DummyNetworkForStaticPatl(df)
        result = build_cgm_static_patl(network)
        assert result["b1"][1] == 1000.0

    def test_excludes_non_line_transformer_element_types(self):
        df = _make_operational_limits_df([
            dict(element_id="b1", side="ONE", type="CURRENT", acceptable_duration=-1,
                 group_name="g1", element_type="LINE", name="permanent_limit", value=1000.0),
            dict(element_id="b2", side="ONE", type="CURRENT", acceptable_duration=-1,
                 group_name="g2", element_type="SWITCH", name="permanent_limit", value=500.0),
        ])
        network = DummyNetworkForStaticPatl(df)
        result = build_cgm_static_patl(network)
        assert "b1" in result
        assert "b2" not in result

    def test_empty_operational_limits_returns_empty_dict(self):
        network = DummyNetworkForStaticPatl(pd.DataFrame())
        result = build_cgm_static_patl(network)
        assert result == {}


# ---------------------------------------------------------------------------
# build_pst_degrees_per_tap
# ---------------------------------------------------------------------------


class DummyNetworkForDegreesPerTap:
    def __init__(self, steps_df: pd.DataFrame):
        self._steps_df = steps_df

    def get_phase_tap_changer_steps(self):
        return self._steps_df


class TestBuildPstDegreesPerTap:
    def test_linear_steps_give_exact_average(self):
        """PhaseTapChangerLinear: alpha should scale exactly linearly with
        step, so the computed average should equal the true increment
        exactly, with no non-uniformity warning."""
        # 5 steps: -2, -1, 0, 1, 2 degrees -> exactly 1.0 deg/step
        df = pd.DataFrame([
            {"id": "pst1", "alpha": -2.0},
            {"id": "pst1", "alpha": -1.0},
            {"id": "pst1", "alpha": 0.0},
            {"id": "pst1", "alpha": 1.0},
            {"id": "pst1", "alpha": 2.0},
        ]).set_index("id")
        network = DummyNetworkForDegreesPerTap(df)
        result = build_pst_degrees_per_tap(network, ["pst1"])
        assert result["pst1"] == pytest.approx(1.0)

    def test_out_of_position_order_rows_still_give_correct_average(self, caplog):
        """Rows of the steps table in non-monotonic position order (-1, 0, -2, 1, -3, 2, ...)
        still give the true average (alpha = 2.0 x position) and no non-uniformity warning:
        the rows are sorted by tap position first."""
        df = pd.DataFrame([
            {"id": "pst1", "position": -1, "alpha": -2.0},
            {"id": "pst1", "position": 0, "alpha": 0.0},
            {"id": "pst1", "position": -2, "alpha": -4.0},
            {"id": "pst1", "position": 1, "alpha": 2.0},
        ]).set_index(["id", "position"])
        network = DummyNetworkForDegreesPerTap(df)

        with caplog.at_level("WARNING"):
            result = build_pst_degrees_per_tap(network, ["pst1"])

        assert result["pst1"] == pytest.approx(2.0)
        assert "not uniformly spaced" not in caplog.text

    def test_missing_pst_omitted_not_defaulted(self):
        df = pd.DataFrame([
            {"id": "pst1", "alpha": -1.0},
            {"id": "pst1", "alpha": 1.0},
        ]).set_index("id")
        network = DummyNetworkForDegreesPerTap(df)
        result = build_pst_degrees_per_tap(network, ["pst1", "pst2"])
        assert "pst1" in result
        assert "pst2" not in result

    def test_single_step_pst_omitted(self):
        """A PST with fewer than 2 steps is omitted (logged), not defaulted to 0."""
        df = pd.DataFrame([
            {"id": "pst1", "alpha": 0.0},
        ]).set_index("id")
        network = DummyNetworkForDegreesPerTap(df)
        result = build_pst_degrees_per_tap(network, ["pst1"])
        assert "pst1" not in result

    def test_no_alpha_column_returns_empty(self):
        df = pd.DataFrame([{"id": "pst1", "rho": 1.0}]).set_index("id")
        network = DummyNetworkForDegreesPerTap(df)
        result = build_pst_degrees_per_tap(network, ["pst1"])
        assert result == {}

    def test_missing_steps_table_returns_empty(self):
        class BrokenNetwork:
            def get_phase_tap_changer_steps(self):
                raise RuntimeError("boom")
        result = build_pst_degrees_per_tap(BrokenNetwork(), ["pst1"])
        assert result == {}


# ---------------------------------------------------------------------------
# build_equipment_mrid_to_type
# ---------------------------------------------------------------------------

class DummyNetworkForEquipmentTypes:
    """All 8 pypowsybl accessors build_equipment_mrid_to_type reads, each with a distinct set of
    mRIDs, so every type's attribution is checked."""
    def __init__(self, ids_by_accessor: dict[str, list[str]]):
        self._ids_by_accessor = ids_by_accessor

    def _df(self, accessor_name):
        ids = self._ids_by_accessor.get(accessor_name, [])
        return pd.DataFrame(index=ids)

    def get_lines(self): return self._df("get_lines")
    def get_2_windings_transformers(self): return self._df("get_2_windings_transformers")
    def get_generators(self): return self._df("get_generators")
    def get_loads(self): return self._df("get_loads")
    def get_switches(self): return self._df("get_switches")
    def get_shunt_compensators(self): return self._df("get_shunt_compensators")
    def get_static_var_compensators(self): return self._df("get_static_var_compensators")
    def get_busbar_sections(self): return self._df("get_busbar_sections")


class TestBuildEquipmentMridToType:
    def test_every_accessor_correctly_attributed(self):
        from pre_milp.cgmes_loader import build_equipment_mrid_to_type

        network = DummyNetworkForEquipmentTypes({
            "get_lines": ["line-1"],
            "get_2_windings_transformers": ["xfmr-1"],
            "get_generators": ["gen-1"],
            "get_loads": ["load-1"],
            "get_switches": ["switch-1"],
            "get_shunt_compensators": ["shunt-1"],
            "get_static_var_compensators": ["svc-1"],
            "get_busbar_sections": ["busbar-1"],
        })
        result = build_equipment_mrid_to_type(network)

        assert result == {
            "line-1": "line",
            "xfmr-1": "transformer",
            "gen-1": "gen",
            "load-1": "load",
            "switch-1": "switch",
            "shunt-1": "shuntCompensator",
            "svc-1": "staticVarCompensator",
            "busbar-1": "busbar",
        }

    def test_mrid_not_in_any_accessor_is_absent_not_defaulted(self):
        from pre_milp.cgmes_loader import build_equipment_mrid_to_type

        network = DummyNetworkForEquipmentTypes({"get_lines": ["line-1"]})
        result = build_equipment_mrid_to_type(network)
        assert "unknown-mrid" not in result
        assert result == {"line-1": "line"}

    def test_empty_network_returns_empty_dict(self):
        from pre_milp.cgmes_loader import build_equipment_mrid_to_type

        network = DummyNetworkForEquipmentTypes({})
        result = build_equipment_mrid_to_type(network)
        assert result == {}


_REPO_ROOT_FOR_EQ_TESTS = Path(__file__).resolve().parents[1]


_REAL_CGM_ZIP = Path(__file__).resolve().parent / "fixtures" / "CGM_package.zip"


requires_data_for_eq_tests = pytest.mark.skipif(
    not _REAL_CGM_ZIP.is_file(), reason="tests/fixtures/CGM_package.zip not present",
)


# ===========================================================================
# Initial load flow that does not converge
# ===========================================================================

# ---------------------------------------------------------------------------
# initial load-flow non-convergence halts the run
# (the invalid-exclusionReason halt is test_ae_with_invalid_exclusion_reason_cancels_the_parse)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("status_name", ["FAILED", "MAX_ITERATION_REACHED"])
def test_a_non_converged_initial_load_flow_halts_with_runtime_error_and_a_fatal_log(monkeypatch, caplog, status_name):
    import types
    from pre_milp.cgmes_loader import run_initial_loadflow
    fake_pp = types.ModuleType("pypowsybl")

    class loadflow:
        Parameters = staticmethod(lambda **kw: types.SimpleNamespace(**kw))

        @staticmethod
        def run_ac(network, parameters=None):
            return [types.SimpleNamespace(status=types.SimpleNamespace(name=status_name))]

    fake_pp.loadflow = loadflow
    monkeypatch.setitem(sys.modules, "pypowsybl", fake_pp)
    with caplog.at_level(logging.CRITICAL):
        with pytest.raises(RuntimeError, match="did not converge"):
            run_initial_loadflow(object())
    assert any(r.levelno == logging.CRITICAL and status_name in r.message for r in caplog.records)


# ===========================================================================
# Missing data in the network tables (no silent defaults)
# ===========================================================================

class _FakeNetworkForTables:
    """Network double: DataFrame accessors only; an accessor listed in `failing` raises."""

    def __init__(self, generators=None, lines_results=None, ratio_tap_changers=None, failing=()):
        self._generators = generators if generators is not None else pd.DataFrame()
        self._lines_results = lines_results
        self._ratio_tap_changers = ratio_tap_changers
        self._failing = set(failing)

    def _maybe_fail(self, name):
        if name in self._failing:
            raise RuntimeError(f"{name} failed (test)")

    def get_lines(self):
        self._maybe_fail("get_lines")
        return pd.DataFrame(index=pd.Index([], name="id"))

    def get_lines_results(self):
        return self._lines_results

    def get_2_windings_transformers(self):
        return pd.DataFrame(index=pd.Index([], name="id"))

    def get_2_windings_transformers_results(self):
        return pd.DataFrame(index=pd.Index([], name="id"))

    def get_phase_tap_changers(self):
        return pd.DataFrame(index=pd.Index([], name="id"))

    def get_ratio_tap_changers(self):
        return self._ratio_tap_changers

    def get_generators(self):
        self._maybe_fail("get_generators")
        return self._generators


def test_a_generator_without_pmax_and_pmin_gets_zero_limits_with_one_warning_through_the_pipeline_path(tmp_path, caplog):
    from pre_milp import cgmes_loader, ncp_parser
    from data_model import BidDirection, PowerBid
    from milp.milp_builder import RdMilpInputs, build_n0_milp_model
    from helpers import _write_penalty_factor_ra, _make_ae_mb_scanned
    from data_model import AEType
    generators = pd.DataFrame(
        {"target_p": [50.0], "max_p": [float("nan")], "min_p": [float("nan")]},
        index=pd.Index(["GU1"], name="id"),
    )
    with caplog.at_level(logging.WARNING):
        _, _, generating_units = cgmes_loader.extract_equipment_dicts(_FakeNetworkForTables(generators=generators))
    assert generating_units["GU1"]["max_p"] == 0.0 and generating_units["GU1"]["min_p"] == 0.0
    warnings = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING and "GU1" in r.getMessage()]
    assert len(warnings) == 1
    body = """
    <nc:GridStateAlterationRemedialAction rdf:ID="_RA1">
      <cim:IdentifiedObject.mRID>RA1</cim:IdentifiedObject.mRID>
      <nc:RemedialAction.normalAvailable>true</nc:RemedialAction.normalAvailable>
      <nc:RemedialAction.kind rdf:resource="https://cim4.eu/ns/nc#RemedialActionKind.preventive"/>
      <nc:RemedialAction.penaltyFactor>1.0</nc:RemedialAction.penaltyFactor>
    </nc:GridStateAlterationRemedialAction>
    <nc:RotatingMachineAction rdf:ID="_RMA1">
      <nc:GridStateAlteration.GridStateAlterationRemedialAction rdf:resource="#_RA1"/>
      <nc:RotatingMachineAction.RotatingMachine rdf:resource="#_GU1"/>
    </nc:RotatingMachineAction>
    """
    rd_units, _ = ncp_parser.parse_rd_units(
        _write_penalty_factor_ra(tmp_path, body), None, "TSO", "1030Z", generating_units,
    )
    assert (rd_units[0].max_p, rd_units[0].min_p) == (0.0, 0.0)
    bid = PowerBid(
        mrid="BID1", ra_mrid="RA1", direction=BidDirection.UP, available_mw={"1030Z": 10.0},
        price_eur_mw=1.0, lead_time_h=0.0, activation_cost_eur=None,
    )
    model = build_n0_milp_model(
        [_make_ae_mb_scanned("B1", AEType.SECURED, 1, 1.0)], "1030Z", {"B1": {1: 500.0}}, 1000.0,
        rd_inputs=RdMilpInputs(
            rd_list=rd_units, bid_list=[bid], glsk={"RA1": {"GU1": 1.0}},
            sensitivity_rd_n0_pruned={("B1", "GU1"): 1.0}, generator_data=generating_units,
        ),
    )
    assert model.pmax_pmin_constraint["GU1"].upper == 0.0


def test_a_failing_accessor_in_extract_equipment_dicts_is_logged(caplog):
    from pre_milp import cgmes_loader
    with caplog.at_level(logging.ERROR):
        cgmes_loader.extract_equipment_dicts(_FakeNetworkForTables(failing=("get_generators",)))
    assert any("get_generators failed" in (r.exc_text or "") + r.getMessage() or r.exc_info for r in caplog.records)


def test_a_missing_current_column_is_nan_not_zero_with_a_warning(caplog):
    from pre_milp import cgmes_loader
    lines_results = pd.DataFrame({"i1": [100.0]}, index=pd.Index(["L1"], name="id"))
    with caplog.at_level(logging.WARNING):
        lf = cgmes_loader.build_lf_initial(_FakeNetworkForTables(lines_results=lines_results))
    assert lf["L1"][1] == 100.0
    assert lf["L1"][2] != lf["L1"][2], "missing side-2 current must be NaN"
    assert any("L1" in r.getMessage() and r.levelno == logging.WARNING for r in caplog.records)


def test_a_ratio_tap_changer_at_tap_zero_keeps_tap_zero():
    from pre_milp import cgmes_loader
    item = types.SimpleNamespace(id="RTC1", tap=0, low_tap=-5, high_tap=5)
    # a generator, not a list: the non-DataFrame path is taken only for objects without .index
    _, tap_changers, _ = cgmes_loader.extract_equipment_dicts(
        _FakeNetworkForTables(ratio_tap_changers=(entry for entry in [item])),
    )
    assert tap_changers["RTC1"] == {"low_tap": -5, "high_tap": 5, "tap": 0}


# ---------------------------------------------------------------------------
# limits of inactive limit groups
# ---------------------------------------------------------------------------

class DummyNetworkWithLimitGroups:
    """get_operational_limits(): the selected groups only; show_inactive_sets=True: all the groups."""

    def __init__(self, rows: list[dict]):
        self._all = _make_operational_limits_df(rows)
        selected = [r for r in rows if r["selected"]]
        self._selected = _make_operational_limits_df(selected) if selected else self._all.iloc[0:0]

    def get_operational_limits(self, show_inactive_sets=False):
        return self._all if show_inactive_sets else self._selected


def _group_row(element_id, side, group, value, selected=False, duration=-1):
    return dict(element_id=element_id, side=side, type="CURRENT", acceptable_duration=duration, group_name=group,
                element_type="LINE", name="limit", value=value, selected=selected)


class TestInactiveLimitGroups:
    def test_same_permanent_limit_in_all_groups_is_used(self, caplog):
        rows = [_group_row("synthetic_line_a", "ONE", g, 900.0) for g in ("g1", "g2", "g3")]
        rows.append(_group_row("synthetic_line_a", "TWO", "g1", 700.0, selected=True))
        network = DummyNetworkWithLimitGroups(rows)
        with caplog.at_level(logging.INFO):
            result = build_cgm_static_patl(network)
        assert result["synthetic_line_a"] == {1: 900.0, 2: 700.0}
        assert "1 branch side(s) without a selected limit group" in caplog.text

    def test_different_permanent_limits_give_no_patl_and_are_counted(self, caplog):
        rows = [_group_row("synthetic_line_b", "ONE", g, v) for g, v in (("g1", 600.0), ("g2", 900.0), ("g3", 1200.0))]
        rows.append(_group_row("synthetic_line_b", "TWO", "g1", 700.0, selected=True))
        network = DummyNetworkWithLimitGroups(rows)
        with caplog.at_level(logging.INFO):
            result = build_cgm_static_patl(network)
        assert result["synthetic_line_b"] == {2: 700.0}
        assert "1 branch side(s) have limit groups with different permanent limits" in caplog.text
        assert "ratio 2 to 2" in caplog.text
        assert "synthetic_line_b side 1" in caplog.text

    def test_selected_group_keeps_its_value(self):
        rows = [_group_row("synthetic_line_c", "ONE", "g1", 500.0, selected=True),
                _group_row("synthetic_line_c", "ONE", "g2", 800.0)]
        result = build_cgm_static_patl(DummyNetworkWithLimitGroups(rows))
        assert result["synthetic_line_c"] == {1: 500.0}

    def test_tatls_are_used_only_when_all_groups_agree(self):
        from pre_milp.cgmes_loader import build_branch_limits
        rows = []
        for g in ("g1", "g2"):
            rows += [_group_row("synthetic_line_d", "ONE", g, 900.0), _group_row("synthetic_line_d", "ONE", g, 1100.0, duration=600)]
        rows += [_group_row("synthetic_line_e", "ONE", "g1", 900.0), _group_row("synthetic_line_e", "ONE", "g1", 1100.0, duration=600),
                 _group_row("synthetic_line_e", "ONE", "g2", 900.0), _group_row("synthetic_line_e", "ONE", "g2", 1300.0, duration=600)]
        table = build_branch_limits(DummyNetworkWithLimitGroups(rows))
        tatl = table[table["acceptable_duration"] > 0]
        assert list(tatl["branch_id"]) == ["synthetic_line_d"]
        assert list(tatl["value"]) == [1100.0]
        assert sorted(table.loc[table["acceptable_duration"] == -1, "branch_id"]) == ["synthetic_line_d", "synthetic_line_e"]
