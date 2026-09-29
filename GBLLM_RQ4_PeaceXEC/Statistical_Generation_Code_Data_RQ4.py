import argparse
from pathlib import Path

import pandas as pd


def first_existing_column(dataframe, candidates, description):
    for column in candidates:
        if column in dataframe.columns:
            return column
    raise ValueError(f"Could not find {description}. Tried: {', '.join(candidates)}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Report the repository-level RQ4 optimization cases."
    )
    parser.add_argument(
        "--dataset-path",
        required=True,
        help="Path to the downloaded/generated PEACEXEC result CSV file.",
    )
    parser.add_argument(
        "--minimum-improvement",
        type=float,
        default=0.10,
        help="Minimum relative runtime reduction counted as an improvement (default: 0.10).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    dataset_path = Path(args.dataset_path).expanduser()
    if not dataset_path.is_file():
        raise FileNotFoundError(f"Dataset CSV not found: {dataset_path}")

    dataframe = pd.read_csv(dataset_path)
    id_column = first_existing_column(
        dataframe, ["repo_unique_id", "Repo_Unique_ID"], "repository case-ID column"
    )
    repository_column = first_existing_column(
        dataframe, ["reponame", "repo_path", "repository"], "repository-name column"
    )
    original_time_column = first_existing_column(
        dataframe, ["input__time(us)"], "original execution-time column"
    )
    medium_time_column = first_existing_column(
        dataframe,
        ["epoch4__mid_time", "Cot_NL_CFG_SlowMidFast_Round4_Sorted_MidTime"],
        "medium-candidate execution-time column",
    )
    fast_time_column = first_existing_column(
        dataframe,
        ["epoch4__fast_time", "Cot_NL_CFG_SlowMidFast_Round4_Sorted_FastTime"],
        "fast-candidate execution-time column",
    )

    original_times = pd.to_numeric(dataframe[original_time_column], errors="coerce")
    candidate_times = pd.concat(
        [
            pd.to_numeric(dataframe[medium_time_column], errors="coerce"),
            pd.to_numeric(dataframe[fast_time_column], errors="coerce"),
        ],
        axis=1,
    )
    fastest_times = candidate_times.min(axis=1, skipna=True)
    valid = original_times.notna() & fastest_times.notna() & (original_times > 0) & (fastest_times > 0)
    improvement = (original_times - fastest_times) / original_times
    improved = valid & (improvement >= args.minimum_improvement)

    summary = (
        dataframe.assign(_valid=valid, _improved=improved)
        .groupby(repository_column, dropna=False)
        .agg(Cases=(id_column, "size"), Valid_cases=("_valid", "sum"), Improved_cases=("_improved", "sum"))
        .reset_index()
        .sort_values(repository_column)
    )

    print(f"Total CSV rows: {len(dataframe)}")
    print(f"Cases with measurable candidate times: {int(valid.sum())}")
    print(
        f"Cases at least {args.minimum_improvement:.0%} faster than the original: "
        f"{int(improved.sum())}"
    )
    print("\nPer-repository summary:")
    print(summary.to_string(index=False))

    if improved.any():
        details = dataframe.loc[improved, [id_column, repository_column]].copy()
        details["Original_time_us"] = original_times.loc[improved]
        details["Best_candidate_time_us"] = fastest_times.loc[improved]
        details["Speedup_x"] = (original_times.loc[improved] / fastest_times.loc[improved]).round(2)
        print("\nImproved cases:")
        print(details.to_string(index=False))


if __name__ == "__main__":
    main()
