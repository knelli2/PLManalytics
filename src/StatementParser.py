import datetime as dt
import json
import os
import sys
from glob import glob

import pandas as pd

import Utilities as UT
import VersionChecker as VC
from src.Global import RAW_STATEMENT_DIR

# Identifies each image uniquely
master_index = "Asset Number"
# Identifies each individual image order uniquely
secondary_index = "Invoice Number"
indices = [master_index, secondary_index]

# Columns of data to take from the earning statements
other_columns = [
    "Name",
    "Contact ID",
    "Contract ID",
    "Contract Name",
    "Royalty Month",
    "Sales Date",
    "Sale Region",
    "Customer Name",
    "Alternate Asset Number",
    "Asset Description",
    "Rights: Industry",
    "Rights Usage",
    "Sales Territory",
    "License Fee in USD",
    "Royalty Rate",
    "Gross Royalty in USD",
    "Royalty Pay Date",
    "Contributors Net payment (summary for full stmt)",
    "StatementSummary_US_NetPayment",
    "StatementSummary_US_NetPaymentInCurrency",
    "StatementSummary_NonUS_NetPaymentInCurrency"
]

column_types = [
    str,
    int,
    int,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    float,
    float,
    float,
    str,
    float,
    float,
    float,
    float
]

# All columns. Indices plus data
all_columns = indices + other_columns


# Function to make negative string values positive floats. Some values in the
# earning statements are negative when they should be positive
def str_abs(str_val):
    return abs(float(str_val))


# Dictionary of functions for converting values in the earning statements to a
# more desirable format
converters = {
    "License Fee in USD": str_abs,
    "Gross Royalty in USD": str_abs,
}


# Actually reads all the earning statements and concats them into one large
# DataFrame
def generate_global_df_unorganized(statement_directory):
    all_files_path = os.path.join(statement_directory, "*.txt")
    statement_files = glob(all_files_path)

    if not len(statement_files) > 0:
        sys.exit(
            f"There are no statement files in the {statement_directory} to "
            "read. Check that you have a directory named "
            "'raw_earning_statements' in the `db` directory in the root of the"
            " repository. This directory holds all the txt earning statements."
        )

    df_list = [
        pd.read_csv(
            name,
            sep="\t",
            encoding="utf-8-sig",
            index_col=indices,
            usecols=all_columns,
            converters=converters,
        ) for name in statement_files
    ]

    return pd.concat(df_list, ignore_index=False, levels=indices, copy=False)


# Organizes a DataFrame from generate_global_df_unorganized with multiple
# indices defined by the master index and secondary index defined at the top of
# this file. Inspired by this stack overflow post:
# https://stackoverflow.com/questions/52923685/convert-pandas-multiindex-series-to-json-python
def organize_df(unorganized_df):
    group1 = (
        # This line creates a DF object where the entries are grouped first by
        # the master_index. Then underneath that, if there are multiple
        # entires with the same master index, each sub entry, which is organized
        # by the secondary index, contains the rest of that data
        unorganized_df.groupby(indices)[other_columns]
        # This line makes the data associated with each sub entry a list of
        # dictionaries for each sub entry
        .apply(lambda x: x.to_dict("records"))
        # This line associates the list that was just created for each sub entry
        # with the index "data" that can be referenced just like the master
        # index or secondary index
        .reset_index(name="data")
        # This line creates a DF object where now each master index corresponds
        # to a grouped object which is indexed by the secondary index. Each
        # secondary index is associated with the corresponding dictionary from
        # the "data" list in the previous line
        .groupby(master_index)[[secondary_index, "data"]]
        # This line associates each master index with a dictionary. The keys of
        # the dictionary are the secondary index, the values are the "data"
        .apply(lambda x: x.set_index(secondary_index)["data"].to_dict()))

    return group1


# Takes an organized DataFrame and writes it a json file. If pretty==True, will
# print everything with indents so it is human readable. If not, then it's just
# the default output of json.dump(). When a file is written, a version file is
# also written
def write_df_to_json(df, filename, pretty=False):
    outfile = open(filename, "w+")

    json_str = df.to_json()
    # The reason we do this replace is because the original data comes in
    #
    # Master: {
    #   Secondary: [
    #     {data}
    #   ],
    #   Secondary: [
    #     {data}
    #   ]
    # }
    #
    # But those extra [] are completely unnecessary as they only wrap the actual
    # data in a list. So we'd always have to do data[0] to get the actual data.
    # I couldn't figure out how to make them go away in the DF manipulation, so
    # we just get rid of the with string replacement and it works just fine.
    json_str = json_str.replace("[{", "{").replace("}]", "}")

    json_dict = json.loads(json_str)

    if pretty:
        json.dump(json_dict, outfile, indent=2)
    else:
        json.dump(json_dict, outfile)

    outfile.close()

    out_dir = UT.get_directory(filename)
    VC.write_version(out_dir)

# Expects the statement files to be named /path/to/YYYYMM-*.txt
def get_year_month_from_statement_file(statement_file):
    raw_str = statement_file.split("/")[-1].split("-")[0]
    result = dt.datetime.strptime(raw_str, "%Y%m").strftime("%Y-%b")
    return result


# Read in all earning statements from the given directory and write then to a
# json file with the given name. If pretty==True, will print everything with
# indents so it is human readable. If not, then it's just the default output of
# json.dump(). If the version file hasn't changed, then don't recompute anything
def parse_and_write_earning_statements(statement_directory,
                                       outfile_name,
                                       pretty=False):
    if not VC.has_version_changed(statement_directory):
        return

    unorganized_df = generate_global_df_unorganized(statement_directory)

    organized_df = organize_df(unorganized_df)

    write_df_to_json(organized_df, outfile_name, pretty)


# Returns a list of dictionaries where the "_id" of each dict is the image id
# and there is one entry "purchases" which has a list of dicts corresponding to
# every time that image was sold
def read_earning_statement(statement_file):
    images = []
    royalty_month = get_year_month_from_statement_file(f)

    with open(statement_file, "r", encoding='utf-8-sig') as f:
        columns = f.readline().strip().split("\t")
        past_header = False
        for line in f.readlines():
            if not past_header:
                past_header = True
                continue

            data = line.split("\t")

            id_idx = columns.index(master_index)
            invoice_idx = columns.index(secondary_index)

            invoice_info = {}
            invoice_info[secondary_index] = data[invoice_idx]
            for value,func in zip(other_columns, column_types):
                idx = columns.index(value)
                invoice_info[value] = func(data[idx])
                if func == float and invoice_info[value] < 0.0:
                    invoice_info[value] *= -1.0
            
            # Reset "Royalty Month" to be a consistent format
            invoice_info["Royalty Month"] = royalty_month

            image_id = data[id_idx]
            image_exists_idx = next(
                (i
                 for i, item in enumerate(images) if item["_id"] == image_id),
                None)
            if image_exists_idx == None:
                images.append({"_id": image_id, "purchases": [invoice_info]})
            else:
                images[image_exists_idx]["purchases"].append(invoice_info)

    return images
