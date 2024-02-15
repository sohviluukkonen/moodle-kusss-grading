Scripts that automatically create grading files (that can be imported in KUSSS) based on Moodle grading exports and KUSSS course participant exports.

1. Download grades from Moodle as csv (i.e. "Plain text file")
2. Download KUSSS participant files for each group from KUSSS as csv
3. Create a grading script. The only things you need to modify are (i) the `_create_grade_row` method to match your grading rules and (ii) the inclusion or not of `_process_entries`.

```
import numpy as np
import pandas as pd

from graders import util
from graders.grader import Grader

MAX_POINTS = 100

class YourGrader(Grader):

    # Only in cases when grade based on Assignments
    def _process_entries(self, df: pd.DataFrame) -> pd.DataFrame:
        len_before = len(df)
        df.dropna(how="all", subset=self.assignment_cols, inplace=True)
        if len_before != len(df):
            self._print(f"dropped {len_before - len(df)} entries due to all assignments being NaN (no participation in "
                        f"the assignments at all)")
        return df
    
    def _create_grade_row(self, row: pd.Series) -> pd.Series:
        """Grade a row/student from the moodle grade file based on Grading rules"""
        # only one assignment can be skipped or graded with 0 points
        # replace 0 points with NaN to make things easier with pd.Series.isna()
        assignment_points = row[self.assignment_cols].replace(0, np.nan)
        if assignment_points.isna().sum() > 1:
            return pd.Series([5, "more than 1 assignment skipped/graded with 0 points"])
        return util.create_grade(assignment_points.sum(), MAX_POINTS)


if __name__ == "__main__":
    args = util.get_grading_args_parser().parse_args()
    util.args_sanity_check(args.moodle_file, args.kusss_participants_files)
    assert args.grading_file is None, "not supported since all KUSSS participants files are treated individually"
    grader = YourGrader(args.moodle_file)
    for kusss_participants_file in args.kusss_participants_files:
        try:
            gdf, gf = grader.create_grading_file(kusss_participants_file)
            gdf.to_csv(gf.replace(".csv", "_FULL.csv"), index=False)
        except ValueError as e:
            print(f"### ignore file '{kusss_participants_file}' because of '{e}'")
        print()
```

4. Grade: `python your_grader.py -mf <moodle_grade_file> -kpf <kusss_participant_file>`
5. Import output file to KUSSS.

5. If you want to grade multiple UE groups in parallel here is a helper script:
```
#!/bin/bash

# Get all file paths starting with WS2_PP1_365 in PP1_exercise_grades
files=$(find <folder_name> -type f -name '<kusss_file_prefix>' | grep -v 'grading')

echo $files

# Loop through each file and execute the python command
for file in $files; do
    python python1exercisegrader.py -mf <moodle_grade_file> -kpf "$file"
done
```
