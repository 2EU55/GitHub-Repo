from src.data_handler import generate_sample_data
from src.calculator import calculate_bonus, check_forced_distribution, check_department_budget
from src.ai_analysis import generate_analysis_report
from src.schema import build_standard_df, validate_df
from src.storage import init_db, save_scenario, load_scenario, list_scenarios, delete_scenario


def main():
    df = generate_sample_data(20)
    weights = {"S": 2.0, "A": 1.5, "B": 1.0, "C": 0.5, "D": 0.0}
    df2 = calculate_bonus(df, 1000000, weights)
    assert "预估奖金" in df2.columns
    assert df2["预估奖金"].sum() > 0

    warnings = check_forced_distribution(df2, s_limit=0.2, sa_limit=0.4)
    assert isinstance(warnings, list)

    budgets = {dept: 10.0 for dept in df2["部门"].unique()}
    budget_warnings = check_department_budget(df2, budgets)
    assert isinstance(budget_warnings, list)

    report = generate_analysis_report(df2)
    assert isinstance(report, str) and len(report) > 0

    raw_df = df2.rename(columns={"当前薪资": "salary"})
    mapped = build_standard_df(raw_df, {"当前薪资": "salary"})
    v = validate_df(mapped)
    assert isinstance(v, dict) and "errors" in v and "warnings" in v

    init_db()
    params = {"total_bonus_pool": 123, "weight_s": 2}
    save_scenario("smoke_scenario", params, mapped)
    names = list_scenarios()
    assert "smoke_scenario" in names
    p2, d2 = load_scenario("smoke_scenario")
    assert p2["total_bonus_pool"] == 123
    assert len(d2) == len(mapped)
    delete_scenario("smoke_scenario")


if __name__ == "__main__":
    main()
