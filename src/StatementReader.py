from glob import glob
import sys
import pandas as pd

statement_dir = "earning_statements/"

important_columns = [
    "Name",
    "Royalty Month",
    "Invoice Number",
    "Sales Date",
    "Sale Region",
    "Customer Name",
    "Asset Number",
    "Alternate Asset Number",
    "Asset Description",
    "Sales Territory",
    "Percent of Product",
    "License Fee in USD",
    "Royalty Rate",
    "Gross Royalty in USD",
    "Royalty Pay Date",
    "Contributors Net payment (summary for full stmt)",
    "StatementSummary_US_ContributorsShare",
    "StatementSummary_US_Gross",
    "StatementSummary_US_Net",
    "StatementSummary_US_NetPayment",
    "StatementSummary_US_NetPaymentInCurrency",
    "StatementSummary_NonUS_ContributorsShare",
    "StatementSummary_NonUS_Gross",
    "StatementSummary_NonUS_NetEarnings",
    "StatementSummary_NonUS_Net",
    "StatementSummary_NonUS_NetPayment",
    "StatementSummary_NonUS_NetPaymentInCurrency",
    "StatementSummary_Totals_Gross",
    "StatementSummary_Totals_NetEarnings",
    "StatementSummary_Totals_NetPayment",
]


def column_number(column_name):
    return important_columns.index(column_name)


statement_files = glob(statement_dir + "*.txt")

if not len(statement_files) > 0:
    sys.exit(
        "There are no statement files to read. Check that you have a directory"
        " named 'earning_statements' in the root directory of the repository"
        " that holds all the earning statements."
    )

df_list = [
    pd.read_csv(name, sep="\t", encoding="utf-8-sig")
    for name in statement_files
]

global_df = pd.concat(df_list, ignore_index=True, copy=False)

total_royalty = global_df["Gross Royalty in USD"].sum()

asset_descriptions_raw = global_df["Asset Description"].tolist()
# The first 10 characters of the description is a unique ID every picture has.
# This ID can be used to track specific pictures.
unique_image_id = [int(x[0:10]) for x in asset_descriptions_raw]

print(total_royalty)
print(unique_image_id)
