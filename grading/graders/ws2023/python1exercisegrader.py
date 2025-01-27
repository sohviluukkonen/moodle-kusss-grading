import numpy as np
import pandas as pd

import sys
sys.path.append('../..')

from graders import util
from graders.grader import Grader

MAX_POINTS_EXAM = 100
MAX_POINTS_A = 100  # all assignments have 100 points (except the bonus assignment (50) which we can ignore here)
N_ASSIGNMENTS = 10
MAX_POINTS_ALL_A = N_ASSIGNMENTS * MAX_POINTS_A
MAX_POINTS = MAX_POINTS_EXAM + MAX_POINTS_ALL_A
MAX_N_ASSIGNMENTS_FAILED = 2

THRESHOLD_EXAM = 0.5
THRESHOLD_INDIVIDUAL_A = 0.25
THRESHOLD_ALL_A = 0.5

PLAGIA_LIST = pd.read_csv("python1plagiarism.csv")['ID number'].tolist()

class Python1ExerciseGrader(Grader):
    
    def _process_entries(self, df: pd.DataFrame) -> pd.DataFrame:
        len_before = len(df)
        df.dropna(how="all", subset=self.assignment_cols, inplace=True)
        if len_before != len(df):
            self._print(f"dropped {len_before - len(df)} entries due to all assignments being NaN (no participation in "
                        f"the assignments at all)")
        return df
    
    def _plagiarism(self, id_number: str) -> list[str]:
        return True if int(id_number) in PLAGIA_LIST else False
    
    def _create_grade_row(self, row: pd.Series) -> pd.Series:
        # assignments processing (if students already failed the course via some assignment rule, there is no need to
        # even look at the exam, since it will not make a difference anymore, i.e., assignment fails are a "hard" fail
        # (unchangeable grade 5), while exam fails are a "soft" fail (can be potentially corrected by a retry exam)
        points = []
        n_failed = 0

              
        if self._plagiarism(row["ID number"][1:]):
            return pd.Series([5, "too many plagiarised assignments"])
        
        for i in range(N_ASSIGNMENTS):
            a_points = row[f"Assignment: Assignment {i + 1} (Real)"]
            if np.isnan(a_points):
                a_points = 0
            points.append(a_points)
            if a_points < MAX_POINTS_A * THRESHOLD_INDIVIDUAL_A:
                n_failed += 1

        a_points = sum(points)
        
        # Due to mismacth before info on slides and Moodle -> Bonus assignent should be counted already here
        bonus_points = row["Assignment: Assignment 11 (Bonus) (Real)"]
        if not np.isnan(bonus_points):
            a_points += bonus_points
            if bonus_points >=  MAX_POINTS_A * THRESHOLD_INDIVIDUAL_A:
                n_failed -=1
        
        if n_failed > MAX_N_ASSIGNMENTS_FAILED:
            return pd.Series([5, f"more than {MAX_N_ASSIGNMENTS_FAILED} individual assignment thresholds not reached"])
        
        
        if a_points < MAX_POINTS_ALL_A * THRESHOLD_ALL_A:
            return pd.Series([5, "total assignment threshold not reached"])
        
        # exam processing
        e1 = row["Quiz: Exam (Real)"]
        e2 = row["Quiz: Retry Exam (Real)"]
        e3 = row["Quiz: Retry Exam 2 (Real)"]
        # most recent exam takes precedence
        if not np.isnan(e3):
            e_points = e3
        elif not np.isnan(e2):
            # +(2.5 / 3) points due to misleading answer in one question
            e_points = e2 + (2.5 / 3)
        elif not np.isnan(e1):
            # +(2.5 / 3) points due to misleading answer in one question
            e_points = e1 + (2.5 / 3)
        else:
            return pd.Series([5, "no exam participation"])
        if e_points < MAX_POINTS_EXAM * THRESHOLD_EXAM:
            return pd.Series([5, "exam threshold not reached"])
        
        # # only now add bonus points (after all requirement checks from above)
        # bonus_points = row["Assignment: Assignment 11 (Bonus) (Real)"]
        # if not np.isnan(bonus_points):
        #     a_points += bonus_points
        
        return util.create_grade(e_points + a_points, MAX_POINTS)


if __name__ == "__main__":
    args = util.get_grading_args_parser().parse_args()
    # util.args_sanity_check(args.moodle_file, args.kusss_participants_files)
    assert args.grading_file is None, "not supported since all KUSSS participants files are treated individually"
    grader = Python1ExerciseGrader(args.moodle_file)
    for kusss_participants_file in args.kusss_participants_files:
        try:
            gdf, gf = grader.create_grading_file(kusss_participants_file)
            gdf.to_csv(gf.replace(".csv", "_FULL.csv"), index=False)
        except ValueError as e:
            print(f"### ignore file '{kusss_participants_file}' because of '{e}'")
        print()
