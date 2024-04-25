#!/bin/bash

# Define arrays for identifiers, project names, and number of bugs
identifiers=("Lang")
project_names=("lang")
n_bugs=(64)

# Loop through each project
for ((i=0; i<${#identifiers[@]}; i++)); do
    
    for ((nb=3; nb<=${n_bugs[$i]}; nb++)); do
        
        # Navigate to the project directory
        cd "/home/ingridmarcal/Documents/PrimeiraGeracao/${project_names[$i]}/${project_names[$i]}_${nb}_buggy/"
        
        # Rename the folder
        rm -R "budgets.txt"
    done
done
