#!/bin/bash

# Define arrays for identifiers, project names, and number of bugs
identifiers=("Time")
project_names=("joda-time")
n_bugs=(27)
n_versions=(1)

# File to store the results
output_file="/home/ingridmarcal/Documents/statistics_time.txt"

# Initialize total LOC variable
total_loc=0

# Loop through each project
for ((i=0; i<${#identifiers[@]}; i++)); do
    echo "------------------------------------------------------------------"
    # Create directory for project
    mkdir -p "${project_names[$i]}"
    # Navigate to project directory and perform checkout for the number of bugs that are specified for ((nb=17; nb<=${n_bugs[$i]}; nb++)); do
    for ((nb=1; nb<=${n_bugs[$i]}; nb++)); do
        cd "/home/ingridmarcal/Documents/TerceiraGeracao/${project_names[$i]}/"
        cd "/home/ingridmarcal/Documents/TerceiraGeracao/${project_names[$i]}/${project_names[$i]}_${nb}_buggy/"
        # Generate tests for each version
        for nv in "${n_versions[@]}"; do
            start_time_gen=$(date +%s)
            echo "----------------------------------------------- ${project_names[$i]}_${nb}_buggy version: ${nv} ----------------------------------" | tr '[:lower:]' '[:upper:]' | tee -a "$output_file"
            # Counting total commits up to this version
            total_commits=$(git rev-list --count HEAD)
            echo "Total Commits: $total_commits" | tee -a "$output_file"
            # Accumulate LOC instead of printing each file's LOC
            loc=$(git ls-files | xargs wc -l | awk '{total += $1} END {print total}')
            # Print the total LOC at the end
			echo "Total Lines of Code: $loc" | tee -a "$output_file"
            end_time_gen=$(date +%s)
            execution_time_gen=$((end_time_gen - start_time_gen))
            echo "Test generation time: ${execution_time_gen} seconds" | tee -a "$output_file"
        done
        echo "------------------------------------------------------------------"
        # Navigate back to the main directory
        cd ../..
    done
done
