#!/bin/bash

# Define arrays for identifiers, project names, and number of bugs
identifiers=("Time")
project_names=("joda-time")
n_bugs=(27)
n_versions=(1 2 3 4 5)

# File to store the results
output_file="/home/ingridmarcal/Documents/gen_times.txt"

# Loop through each project
for ((i=0; i<${#identifiers[@]}; i++)); do
	echo "------------------------------------------------------------------"
    # Create directory for project
    mkdir -p "${project_names[$i]}"
	# Navigate to project directory and perform checkout for the number of bugs that are specified
    for ((nb=1; nb<=${n_bugs[$i]}; nb++)); do
        cd "/home/ingridmarcal/Documents/${project_names[$i]}/"
        perl "/home/ingridmarcal/Documents/defects4j/framework/bin/defects4j" checkout -p "${identifiers[$i]}" -v "${nb}b" -w "./${project_names[$i]}_${nb}_buggy"
		cd ../
        cp -v "/home/ingridmarcal/Documents/budgets.txt" "/home/ingridmarcal/Documents/${project_names[$i]}/${project_names[$i]}_${nb}_buggy/budgets.txt"
        cd "/home/ingridmarcal/Documents/${project_names[$i]}/${project_names[$i]}_${nb}_buggy/"
        # Generate tests for each version
        for nv in "${n_versions[@]}"; do
			start_time_gen=$(date +%s)
            perl "/home/ingridmarcal/Documents/defects4j/framework/bin/gen_tests.pl" -g evosuite -p "${identifiers[$i]}" -v "${nb}b" -n "${nv}" -o ./evosuite_tests -b 10
			end_time_gen=$(date +%s)
			execution_time_gen=$((end_time_gen - start_time_gen))
			echo "" | tee -a "$output_file"
			echo "----------------------------------------------- ${project_names[$i]}_${nb}_buggy version: ${nv} ----------------------------------" | tr '[:lower:]' '[:upper:]' | tee -a "$output_file"
			echo "Test generation time: ${execution_time_gen} seconds" | tee -a "$output_file"
        done
		echo "------------------------------------------------------------------"
        # Navigate back to the main directory
        cd ../..
	done
done