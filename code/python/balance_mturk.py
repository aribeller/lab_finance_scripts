import mturk_functions as m
import pandas as pd
import os
from sys import argv

testing = len(argv) > 1 and argv[2] == "--testing"

new_charges_path = argv[1]

if not testing:
	uncleared_charges_path = '../../mturk_sheets/uncleared_charges.csv'
else:
	uncleared_charges_path = "../../mturk_sheets_test/uncleared_charges.csv"


new_charges = pd.read_csv(new_charges_path)
new_charges.sort_values(["Date Initiated", "Assignment ID"])
new_charges["divided"] = ["Full"] * len(new_charges)



if os.path.exists(uncleared_charges_path):
	uncleared_charges = pd.read_csv(uncleared_charges_path)
	charges = pd.concat([uncleared_charges, new_charges])

else:
	charges = new_charges

balanced_sheets, remainder = m.balance_charges(charges)
# sheet_summaries = [sum_sheet(sheet) for sheet in balanced_sheets]
m.make_folders(balanced_sheets, testing=testing)

remainder.to_csv(uncleared_charges_path, index=False)



