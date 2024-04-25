#!/bin/bash

# Define arrays for identifiers, project names, and number of bugs
identifiers=("Lang")
project_names=("commons-lang")
n_bugs=(65)
n_versions=(1 2 3 4 5)

#alias gen_tests_pure=~/Documents/defects4j/framework/bin/gen_tests.pl
#alias defect4j=~/Documents/defects4j/framework/bin/defects4j

# Loop through each project
for ((i=0; i<${#identifiers[@]}; i++)); do
	echo "------------------------------------------------------------------"
    # Create directory for project
    mkdir -p "${project_names[$i]}"
	# Navigate to project directory and perform checkout for the number of bugs that are specified
    for ((nb=1; nb<=${n_bugs[$i]}; nb++)); do
        cd "/home/ingridmarcal/Documents/SegundaGeracao/${project_names[$i]}/"
        perl "/home/ingridmarcal/Documents/defects4j/framework/bin/defects4j" checkout -p "${identifiers[$i]}" -v "${nb}b" -w "./${project_names[$i]}_${nb}_buggy"
		cd ../
        #cp -v "/home/ingridmarcal/Documents/budgets.txt" "/home/ingridmarcal/Documents/SegundaGeracao/${project_names[$i]}/${project_names[$i]}_${nb}_buggy/budgets.txt"
        #cd "/home/ingridmarcal/Documents/SegundaGeracao/${project_names[$i]}/${project_names[$i]}_${nb}_buggy/"
        # Generate tests for each version
        #for nv in "${n_versions[@]}"; do
        #    perl "/home/ingridmarcal/Documents/defects4j/framework/bin/gen_tests.pl" -g evosuite -p "${identifiers[$i]}" -v "${nb}b" -n "${nv}" -o ./evosuite_tests -b 10
        #done
		echo "------------------------------------------------------------------"
        # Navigate back to the main directory
        cd ../..
	done
done