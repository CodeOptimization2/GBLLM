#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: bash Run_Three_Round_Ablation.sh <variant> <dataset.csv> [output-directory]"
  echo "Variants: remove_nl, remove_io, remove_cfg, replace_cfg, remove_time, remove_trajectory, random_effi_cfg, remove_all"
  exit 2
fi

variant="$1"
dataset_path="$2"
output_directory="${3:-Code_Data_Table/three_round_ablation}"
core_number=529
num_threads="${NUM_THREADS:-1}"
mkdir -p "$output_directory"

case "$variant" in
  remove_nl)
    prompt="30_Generate_Code_Ablation_Remove_NL_COT_CFG_Use_IO_Use_Slow_Mid_Fast_Time"
    save_base="Ablation_Remove_NL_Cot_CFG_SlowMidFastTime"
    trajectory_base="Ablation_Remove_NL_Cot_CFG_SlowMidFast"
    ;;
  remove_io)
    prompt="33_Generate_Code_Ablation_Remove_IO_COT_CFG_Use_NL_Use_Slow_Mid_Fast_Time"
    save_base="Ablation_Remove_IO_Cot_NL_CFG_SlowMidFastTime"
    trajectory_base="Ablation_Remove_IO_Cot_NL_CFG_SlowMidFast"
    ;;
  remove_cfg)
    prompt="35_Generate_Code_Ablation_Remove_CFG_COT_CFG_Use_NL_Use_IO_Use_Slow_Mid_Fast_Time"
    save_base="Ablation_Remove_CFG_Cot_NL_SlowMidFastTime"
    trajectory_base="Ablation_Remove_CFG_Cot_NL_SlowMidFast"
    ;;
  replace_cfg)
    prompt="37_Generate_Code_Ablation_Replace_CFG_COT_Use_NL_Use_IO_Use_Slow_Mid_Fast_Time"
    save_base="Ablation_All_CFG_Cot_NL_SlowMidFastTime"
    trajectory_base="Ablation_All_CFG_Cot_NL_SlowMidFast"
    ;;
  remove_time)
    prompt="39_Generate_Code_Ablation_Remove_Time_COT_CFG_Use_NL_Use_IO_Use_Slow_Mid_Fast"
    save_base="Ablation_Remove_Time_Cot_NL_SlowMidFast"
    trajectory_base="Ablation_Remove_Time_Cot_NL_SlowMidFast"
    ;;
  remove_trajectory)
    prompt="40_Generate_Code_Ablation_Remove_Trajectory_COT_CFG_Use_NL_Use_IO"
    save_base="Ablation_Remove_Trajectory_Cot_NL"
    trajectory_base="Ablation_Remove_Trajectory_Cot_NL"
    ;;
  random_effi_cfg)
    prompt="14_Generate_Code_COT_CFG_Use_NL_Use_IO_Use_Slow_Mid_Fast_Time__My_Adopted"
    save_base="Ablation_Random_Effi_CFG_Cot_NL_CFG_SlowMidFastTime"
    trajectory_base="Ablation_Random_Effi_CFG_Cot_NL_CFG_SlowMidFast"
    ;;
  remove_all)
    prompt="49_Generate_Code_Ablation_Remove_All_COT"
    save_base="Ablation_Remove_All_Cot"
    trajectory_base="Ablation_Remove_All_Cot"
    ;;
  *)
    echo "Unknown variant: $variant" >&2
    exit 2
    ;;
esac

working_input="$dataset_path"
if [[ "$variant" == "random_effi_cfg" ]]; then
  working_input="$output_directory/PIE_Py_${variant}_random_cfg.csv"
  python Prepare_Random_Effi_CFG.py \
    --dataset-path "$dataset_path" \
    --output-path "$working_input" \
    --seed 42
elif [[ "$variant" == "remove_io" ]]; then
  nl_base="$output_directory/PIE_Py_${variant}_nl"
  python Large_model_API_generation.py \
    --core_number "$core_number" \
    --prompt_template_name "32_Generate_NL_Ablation_Remove_IO_Long_NL" \
    --baseline_df_path "$dataset_path" \
    --generated_df_path "$nl_base" \
    --iteration_round 0 \
    --num_threads "$num_threads" \
    --num_generated_codes 1 \
    --batch_size 1 \
    --repeat_times 1 \
    --temperature 0.01
  working_input="${nl_base}_DeepSeekV41Flash__32_Generate_NL_Ablation_Remove_IO_Long_NL_.csv"
fi

sorted_input="$output_directory/PIE_Py_${variant}_trajectory_round1.csv"
python Sort_COT_result_codes_by_time.py \
  --dataset_path "$working_input" \
  --save_set_path "$sorted_input" \
  --prepare_round_number 1

history_prefixes="SBLLM_cot_G5"
for round_number in 1 2 3; do
  generated_base="$output_directory/PIE_Py_${variant}_generated_round${round_number}"
  save_prefix="${save_base}_Round${round_number}"
  extra_generation_args=()
  if [[ "$variant" == "remove_io" ]]; then
    extra_generation_args+=(--nl_column "Ablation_Remove_IO_Code_Function_Description_G1")
  elif [[ "$variant" == "random_effi_cfg" ]]; then
    extra_generation_args+=(--cfg-column-name "Random_Effi_CFG")
  fi

  python Large_model_API_generation.py \
    --core_number "$core_number" \
    --prompt_template_name "$prompt" \
    --baseline_df_path "$sorted_input" \
    --generated_df_path "$generated_base" \
    --iteration_round "$round_number" \
    --num_threads "$num_threads" \
    --num_generated_codes 5 \
    --batch_size 1 \
    --repeat_times 5 \
    --temperature 1 \
    --save-column-prefix "$save_prefix" \
    --trajectory-prefix "$trajectory_base" \
    "${extra_generation_args[@]}"

  clean_prompt="${prompt/__My_Adopted/}"
  clean_prompt="${clean_prompt//__/_}"
  generated_csv="${generated_base}_DeepSeekV41Flash__${clean_prompt}_.csv"
  evaluated_csv="$output_directory/PIE_Py_${variant}_evaluated_round${round_number}.csv"
  python PIE__Evaluate_code_execution_time.py \
    --dataset_path "$generated_csv" \
    --save_set_path "$evaluated_csv" \
    --test_io_type "(Public) (Private)" \
    --iteration_round "$round_number" \
    --column-prefix "${save_prefix}_G5"

  history_prefixes="${history_prefixes},${save_prefix}_G5"
  if [[ "$round_number" -lt 3 ]]; then
    next_round=$((round_number + 1))
    sorted_input="$output_directory/PIE_Py_${variant}_trajectory_round${next_round}.csv"
    python Sort_COT_result_codes_by_time.py \
      --dataset_path "$evaluated_csv" \
      --save_set_path "$sorted_input" \
      --prepare_round_number "$next_round" \
      --history-column-prefixes "$history_prefixes" \
      --output-prefix "$trajectory_base"
  fi
done

echo "Completed three rounds: $output_directory/PIE_Py_${variant}_evaluated_round3.csv"
