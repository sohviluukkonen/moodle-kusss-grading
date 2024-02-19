#!/bin/bash

# Get all file paths starting with WS2_PP1_365 in PP1_exercise_grades
files=$(find PP1_exercise_grades -type f -name 'WS23_PP1_365*' | grep -v 'grading')
# files=$(find PP1_exercise_grades_alternative_rules -type f -name 'WS23_PP1_365*' | grep -v 'grading')


echo $files

# Loop through each file and execute the python commandfiles=$(find PP1_exercise_grades -type f -name 'WS23_PP1_365*' | grep -v 'grading')
for file in $files; do
    python python1exercisegrader.py -mf python1moodle.csv -kpf "$file"
    echo
    echo
    # exit
done