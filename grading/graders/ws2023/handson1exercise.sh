#!/bin/bash

# Get all file paths starting with WS2_PP1_365 in PP1_exercise_grades
files=$(find HO1_exercise_grades -type f -name 'WS23_HO1_365*' | grep -v 'grading')

echo $files

# Loop through each file and execute the python command
for file in $files; do
    python handson1exercisegrader.py -mf handson1moodle.csv -kpf "$file"
    echo
done