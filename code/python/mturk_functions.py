import pandas as pd
import numpy as np
import os

# Summary of the algorithm
# Load the spreadsheet. Separate payments from disbursements. For each payment,
# collect disbursements until the payment is cleared. Split official disbursements
# so that the charge is balanced. Mark splits. Package the cleared charge into a 
# separate spreadsheet. Continue to the next payment. Once you run out of disbursements
# or don't have enough disbursements to complete a given payment, collect remaining payments
# and disbursements for future payments

def balance_charges(charges):

	# Split payments and disbursement rows
	payments = charges[charges["Amount"] > 0].reset_index(drop=True)
	disbursements = charges[charges["Amount"] < 0].reset_index(drop=True)

	# Collect disbursement amount
	disb_am = disbursements["Amount"]

	# Track the current disbursement amount
	disb_num = 0

	# For each payment
	sheets = []
	for i in range(len(payments)):
		# grab the row and the payment for the row
		line_item = payments.loc[[i]]
		payment = line_item["Amount"].values[0]
		# set the sheet start index to the current disbursement number
		# initialize an accumulator
		sheet_start = disb_num
		acc = 0
		# while the accumulator hasn't depleted the payment and we haven't made it to the last disbursment
		while round(acc + payment, 2) > 0 and disb_num < len(disb_am):
			# accumulate the payment and up the disbursement index
			# Disbursments are negative
			acc += disb_am[disb_num]
			disb_num += 1


		# Once we've exited the while loop, need to know which exit conditions we hit

		# First check whether we cleared the charge.
		balance = round(acc + payment, 2)
		payment_cleared = not (balance > 0)
		# print(balance)

		if payment_cleared:

			# In the rare case where the disbursements perfectly lined up with the payment,
			# we can quickly clear the charge.
			# Package the balanced charge from the sheet start point to the current payment.
			if balance == 0:
				sheet = pd.concat([line_item, disbursements[sheet_start:disb_num]]).reset_index(drop=True)

			# Otherwise the payment amount was exceeded and we need to balance it by back-tracking
			else:
				# Must have exceeded on the iteration before the last increment (disb_num - 1)
				last_row = disbursements.loc[[disb_num - 1]]
				last_disb = last_row["Amount"].values[0]

				# Balance is a negative value, the amount by which we exceeded the current payment
				# Subtracting balance from the full value of the last disbursement gives us the 
				# amount that that was actually left on the current payment
				# Found some floating point errors so rounding
				partial_disb = round(last_disb - balance, 2)


				# Set the new value for the final row to this partial disbursement
				# and change its status
				last_row["Amount"] = partial_disb
				last_row["divided"] = "Partial"

				# We've partially used up disbursement disb_num - 1, but not completely
				# The amount that we exceeded the current payment (balance) is the amount
				# that is left of the disbursement. Set the amount of that disbursement to
				# that excess and change its status
				disbursements.at[disb_num - 1, "Amount"] = balance
				disbursements.at[disb_num - 1, "divided"] = "Partial"


				# As we proceed we want to make sure we consider the partial disbursement
				# we just created. Decrement the disbursement index to make sure we look
				# at it again
				disb_num -= 1

				# Package the payment with the disbursements array (not including the last row)
				# And the last row that we just created (the partial disbursement)
				sheet = pd.concat([line_item, disbursements[sheet_start:disb_num], last_row]).reset_index(drop=True)

			sheets.append(sheet)

		# Now check if we have exhausted the disbursements remaining.
		# NOTE: we may have exited the while loop having exhausted the disbursements, but
		# the same condition will not pass now because we just decremented the disbursement index
		# in the codeblock above

		no_disp_left = not (disb_num < len(disb_am))

		# If no disbursements are left, take all the remaining payments
		# and any remaining disbursements and package them into a remaining spreadsheet

		# Payments shouldn't be empty if we haven't overdrawn our account
		# Disbursements could be empty, if we perfectly cleared the current payment
		# on the last disbursement. This is unlikely but possible
		# More likely disbursements will still have some leftover charges that don't
		# Make it to the full amount of the current payment. We want to make sure
		# we hold on to those uncleared charges

		if no_disp_left:

			# If we've cleared the current charge, then we start by saving the next payment
			# Otherwise we start with the current payment
			leftover_start = i + 1 if payment_cleared else i

			# EDGE CASE: we've cleared the current charge and there is no next payment
			# i.e the account is at $0.00
			# Also unlikely
			if leftover_start == len(payments):
				return sheets, None

			# Index the remaining payments
			leftover_payments = payments[leftover_start:]

			# Index the remaining disbursements
			leftover_disbursements = disbursements[sheet_start:]

			combined_leftovers = pd.concat([leftover_payments, leftover_disbursements]).reset_index(drop=True)
			combined_leftovers.sort_values(["Date Initiated", "Assignment ID"])

			return sheets, combined_leftovers


def sum_sheet(sheet): 
	summary = sheet.groupby("Transaction Type").sum().round(decimals=2)
	total_row = pd.DataFrame({"Amount": round(summary["Amount"].sum(), 2)}, index=["Total"])
	summary = summary.append(total_row)

	# Specify the preferred order of transaction types
	order = {word: priority for priority, word in enumerate(["Prepayment", "AssignmentPayment", "FeePayment", "BonusPayment", "Total"])}
	sheet_order = sorted(list(summary.index.values), key=lambda x: order[x])

	# return the summary ordered according to that preference order
	return summary.loc[sheet_order]

def make_folders(balanced_sheets, testing):
	# bal_sheets = balanced_sheets(sheets)
	summaries = [sum_sheet(sheet) for sheet in balanced_sheets]

	assert len(balanced_sheets) == len(summaries)

	for sheet, summary in zip(balanced_sheets, summaries):
		date_info_raw = sheet["Date Initiated"][0]
		date_info = date_info_raw.split()[0]
		month, day, year = date_info.split('/')
		# print(date_split)
		date = '-'.join([x.zfill(2) for x in ['20' + year, month, day]])
		# print(date_reorder)
		# date = date.replace('/', '-')
		if not testing:
			path = '../../mturk_sheets/' + date + '_0'
		else:
			path = '../../mturk_sheets_test/' + date + '_0'
		add = 1
		while os.path.isdir(path):
			path = path[:-1]
			path = path + str(add)
			add += 1
		os.mkdir(path)
		sheet.to_csv(path + '/balanced_sheet.csv', index=False)
		summary.to_csv(path + '/summary_sheet.csv')













