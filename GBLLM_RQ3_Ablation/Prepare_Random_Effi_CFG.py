import argparse
import random
import re
from pathlib import Path

import pandas as pd


def load_effi_cfg_candidates(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8").strip()
    starts = [match.start() for match in re.finditer(r"(?m)^# 1(?:\s|\()", text)]
    candidates = [
        text[start:end].strip()
        for start, end in zip(starts, starts[1:] + [len(text)])
    ]
    if len(candidates) != 5:
        raise ValueError(f"Expected five Effi-CFG candidates, found {len(candidates)} in {path}.")
    return candidates


def parse_args():
    parser = argparse.ArgumentParser(
        description="Assign one of five Effi-CFG candidates to each CSV row with replacement."
    )
    parser.add_argument("--dataset-path", required=True, help="Input CSV path.")
    parser.add_argument("--output-path", required=True, help="Output CSV path.")
    parser.add_argument(
        "--effi-cfg-path",
        default=str(Path(__file__).parent / "data" / "Random_Effi_CFG.txt"),
        help="Text file containing the five Effi-CFG candidates.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--column-name", default="Random_Effi_CFG")
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.dataset_path).expanduser()
    output_path = Path(args.output_path).expanduser()
    candidates = load_effi_cfg_candidates(Path(args.effi_cfg_path).expanduser())
    dataframe = pd.read_csv(input_path)
    random_generator = random.Random(args.seed)
    indexed_candidates = list(enumerate(candidates))
    selections = [random_generator.choice(indexed_candidates) for _ in range(len(dataframe))]
    selected_indices = [index for index, _ in selections]
    dataframe[args.column_name] = [candidate for _, candidate in selections]
    dataframe[f"{args.column_name}_Candidate_Index"] = [index + 1 for index in selected_indices]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)
    print(
        f"Saved {len(dataframe)} rows to {output_path}; sampled with replacement "
        f"from five candidates using seed {args.seed}."
    )


if __name__ == "__main__":
    main()
