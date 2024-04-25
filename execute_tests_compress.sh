#!/bin/bash

# Define arrays for identifiers, project names, and number of bugs
identifiers=("Compress")
project_names=("commons-compress")
n_bugs=(47)
n_versions=(1 2 3 4 5)


# File to store the results
output_file="/home/ingridmarcal/Documents/statistical_analisys_exponential/test_budgets_execution_times_compress_dynamosa.txt"

# Loop through each project
for ((i=0; i<${#identifiers[@]}; i++)); do
    
    for ((nb=1; nb<=${n_bugs[$i]}; nb++)); do
        
        cd "/home/ingridmarcal/Documents/TerceiraGeracao/${project_names[$i]}/${project_names[$i]}_${nb}_buggy/"
		echo "" | tee -a "$output_file"
		echo "" | tee -a "$output_file"
		echo "----------------------------------------------- ${project_names[$i]}_${nb}_buggy -----------------------------------------------" | tr '[:lower:]' '[:upper:]' | tee -a "$output_file"
		echo "" | tee -a "$output_file"
		echo "##### DEV TESTS EXECUTION" | tee -a "$output_file"
		start_time_dev=$(date +%s)
        command1_output=$(perl "/home/ingridmarcal/Documents/defects4j/framework/bin/defects4j" test 2>&1)
        end_time_dev=$(date +%s)
        execution_time_dev=$((end_time_dev - start_time_dev))
		
		echo "" | tee -a "$output_file"
		
        echo "$command1_output" | tee -a "$output_file"
		echo "Dev tests execution time: ${execution_time_dev} seconds" | tee -a "$output_file"
		
		echo "" | tee -a "$output_file"
		echo "" | tee -a "$output_file"
		
        echo "##### GEN TESTS EXECUTION" | tee -a "$output_file"
		echo "" | tee -a "$output_file"
        for ((j=0; j<${#n_versions[@]}; j++)); do
			nv=${n_versions[j]}           
            start_time_gen=$(date +%s)
            command2_output=$(perl "/home/ingridmarcal/Documents/defects4j/framework/bin/defects4j" test -s "./evosuite_tests_dynamosa/${identifiers[$i]}/evosuite/$nv/${identifiers[$i]}-${nb}b-evosuite.$nv.tar.bz2" 2>&1) # Adjusted for clarity and correctness
            end_time_gen=$(date +%s)
            execution_time_gen=$((end_time_gen - start_time_gen))
            
			echo "" | tee -a "$output_file"
			
            echo "$command2_output" | tee -a "$output_file"
			echo "Gen tests execution time: ${execution_time_gen} seconds" | tee -a "$output_file"
        done # End of the n_versions loop
		
		echo "" | tee -a "$output_file"
    done
done
