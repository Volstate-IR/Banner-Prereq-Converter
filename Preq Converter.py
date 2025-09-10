import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
from datetime import datetime
import os

def run_script():
    # Select input file
    infile = filedialog.askopenfilename(title="Select input CSV", filetypes=[("CSV Files","*.csv")])
    if not infile:
        return

    now = datetime.now().strftime("%Y_%m_%d %H_%M_%S")

    # Read file
    df = pd.read_csv(infile)

    # Create PRE_REQ_COURSE_ID
    df['PRE_REQ_COURSE_ID'] = np.where(df['PRE_REQ_SUBJECT_CODE'].isna(), np.nan,
                                       df['PRE_REQ_SUBJECT_CODE'] + "_" + df['PRE_REQ_COURSE_NUMBER'])

    # Remove records where a grade or test score exists without a course or test code
    useless_values = df[(df['MIN_GRADE'].notna() & df['PRE_REQ_COURSE_ID'].isna()) |
                        (df['TEST_SCORE'].notna() & df['TEST_CODE'].isna())]
    df = df.drop(useless_values.index)

    internal_banner_variables = ['PRE_REQ_AREA_SET', 'PRE_REQ_AREA_SUBSET', 'PRE_REQ_AREA_RULE']

    # Sort
    df = df.sort_values(by=['COURSE_ID', 'AREA_CODE', 'PRE_REQ_AREA_SET', 'PRE_REQ_AREA_SUBSET']).reset_index(drop=True)

    # Operator logic
    df['OPERATOR'] = np.where(
        df['COURSE_ID'] != df['COURSE_ID'].shift(1),
        None,
        np.where(
            df['PRE_REQ_AREA_SET'] != df['PRE_REQ_AREA_SET'].shift(1),
            'AND',
            np.where(
                df['PRE_REQ_AREA_SUBSET'] == df['PRE_REQ_AREA_SUBSET'].shift(1),
                'AND', 
                'OR'
            )
        )
    )

    # Parenthesis logic
    df['OPEN_PAREN'] = np.where(
        (df['OPERATOR'] == 'OR') &
        (df['COURSE_ID'] == df['COURSE_ID'].shift(-1)) &
        (df['PRE_REQ_AREA_SET'] == df['PRE_REQ_AREA_SET'].shift(-1)) &
        (df['PRE_REQ_AREA_SUBSET'] == df['PRE_REQ_AREA_SUBSET'].shift(-1)) &
        (df['OPERATOR'].shift(-1) == 'AND'),
        '(', ''
    )

    df['CLOSE_PAREN'] = np.where(
        (df['OPERATOR'] == 'AND') &
        (df['COURSE_ID'] == df['COURSE_ID'].shift(1)) &
        (df['PRE_REQ_AREA_SET'] == df['PRE_REQ_AREA_SET'].shift(1)) &
        (df['PRE_REQ_AREA_SUBSET'] == df['PRE_REQ_AREA_SUBSET'].shift(1)) &
        (df['OPERATOR'].shift(1) == 'OR'),
        ')', ''
    )

    # Count and validate
    open_count = (df['OPEN_PAREN'] == '(').sum()
    close_count = (df['CLOSE_PAREN'] == ')').sum()

    if open_count != close_count:
        messagebox.showwarning("Warning", f"Unbalanced parentheses: Open={open_count}, Close={close_count}")
    else:
        messagebox.showinfo("Success", f"Parentheses balanced: Open={open_count}, Closed={close_count}")

    # Set seqno
    df['SEQNO'] = df.groupby('COURSE_ID').cumcount() + 1

    # Select output file
    outdir = filedialog.asksaveasfilename(title="Save output CSV",
                                          defaultextension=".csv",
                                          initialfile=f"output-{now}.csv",
                                          filetypes=[("CSV Files","*.csv")])
    if not outdir:
        return

    df = df[['SEQNO', 'SUBJECT_CODE', 'COURSE_NUMBER', 'COURSE_ID', *internal_banner_variables,
             'OPERATOR', 'OPEN_PAREN', 'PRE_REQ_SUBJECT_CODE', 'PRE_REQ_COURSE_NUMBER', 'PRE_REQ_COURSE_ID', 
             'MIN_GRADE', 'TEST_CODE', 'TEST_SCORE', 'CLOSE_PAREN', 'ALLOW_CONCURRENCY']].drop_duplicates()

    os.makedirs(os.path.dirname(outdir), exist_ok=True)
    df.to_csv(outdir, index=False)
    messagebox.showinfo("Done", f"Output saved to {outdir}")

    root.destroy()

# --- Tkinter GUI ---
root = tk.Tk()
root.title("Banner Prereq Converter")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

label = tk.Label(frame, text="Banner Prereq Converter v2", font=("Arial", 14))
label.pack(pady=(0,10))

email_label = tk.Label(frame, text="Designed by joshua.king@volstate.edu", font=("Arial", 10))
email_label.pack(pady=(0,10))

button = tk.Button(frame, text="Select CSV & Convert", command=run_script, width=25, height=2)
button.pack()

root.mainloop()
