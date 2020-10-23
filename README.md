# lab_finance_scripts
Python scripts to help balance charges for admin.

## Purpose
I wrote this script to try and speed up the process on clearning mturk charges. I found the university's reporting requirements kind of stringent, and I also found it kind of mind-numbing to make sure I tallied up exactly the right amount of charges so that it would balance the amount that we put on the card for an individual purchase. Hopefully you find this helpful too! It's worked for me so far, but it is not robustly tested. If you need any help debugging you can email me at abeller@stanford.edu.


## Dependencies
You'll need a python setup running in your command line with the pandas library installed.
You can install python [here](https://www.python.org/downloads/). Once you have python installed you can use pip to install pandas with the command `pip install pandas`. 


## Instructions
The code is intended to be relatively encapsulated so you don't have to engage with it. In order to balance a spreadsheet, navigate to the code folder then the python folder. Type the following command:

`python balance_mturk.py <spreadsheet_path>`

where spreadsheet_path is the path to the charges spreadsheet you want to balance.

For each HIT purchase in your spreadsheet, Python will make a folder in the mturk_sheets directory titled with the date of the HIT purchase (Year-Month-Day-Index; the index is in case there are multiple HIT purchases from the same day). Each folder will contain a spreadsheet with the HIT purchase at top, followed by all of the payments disbursed to participants and Amazon that "balance" the charge. The folder also contains a summary spreasheet that adds up the subtotals for each expense type (AssignmentPayment, FeePayment, Bonus). Lastly, any leftover charges that don't yet make up enough to balance a HIT purchase will be added to a spreadsheet in mturk_sheets called "uncleared_charges.csv". When you go to clear another spreadsheet down the line, the program will tack on these charges to the beginning of your new spreadsheet, **so make sure your new spreadsheet doesn't overlap with these old charges!**


## Program Details

For each HIT purchase on the spreadsheet, python will collect payments to participants and Amazon, as well as any recorded bonuses and add them up until they reach exactly the amount of the original HIT purchase. If the charges don't match up exactly, such that adding a payment exceeds the total of the HIT purchase, the program will split the charge that exceeds the purchase such that the charge is exactly balanced. The remainder of that charge will be added used to balance the next HIT purchase. Charges that are split in this way are marked "Partial" in the "divided" column of the spreadsheets (unsplit charges are marked "Full"). 

To get a sense of what the output looks like, you look at the sample output in the mturk_sheets_test folder. Their corresponding csv files are in the python folder (test_charges_1/2.csv). In general you can write your own tests and run them using the testing flag from the python script:

`python balance_mturk.py <test_spreadsheet> --testing`

This will write the output to the test directory rather than default mturk_sheets. Be aware for both the testing setting and the normal setting the computation is stateful! It depends on whether or not there is a uncleared_charges.csv file in the sheets folder. If there is it will combine those charges with whatever you feed it, so if you want to test from scratch you will need to delete the uncleared_charges.csv file.


## Last notes
As I say above, haven't had a ton of time to test the program so likely there are edge cases that I'm missing, but all in all I've found this has saved me a lot of time on a task that I found kind of frustrating. So encourage you to try this out if you are interested, and I'm happy to help if there are issues. Feel free to email me at abeller@stanford.edu



