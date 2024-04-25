import csv
import json
import re
import subprocess

# inUse
from datetime import datetime


def assemble_dataset(history_features_path, code_churns_path, project_path):
    history_features = dict()
    dataset = []
    item = []
    print("Joining {} ...".format(project_path))
    with open(history_features_path) as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if row:
                item = [row[0], row[1], row[2], row[3], row[4]]
                with open(code_churns_path) as file2:
                    csvreader2 = csv.reader(file2)
                    for row2 in csvreader2:
                        if row2:
                            if row[0] == row2[0] and row[1] == row2[1]:
                                item.append(row2[2])
                                item.append(row2[3])
                                item.append(row2[4])
                                dataset.append(item)

    print("Saving {} ...".format(project_path))
    save_to_csv_all_features(dataset, project_path)

def save_to_csv_all_features(features, project_path):
    """
    Function to save the history features as a csv file.
    """
    with open(project_path+"/all_features.csv", 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            ["name", "commit", "number_of_authors", "age", "number_unique_changes", "size", "lines_added",
             "lines_deleted"])
        for row in features:
            if row:
                writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]])


if __name__ == "__main__":


	# Path template to be formatted with numbers from 1 to 64
    path_template = "SegundaGeracao/commons-compress/commons-compress_{}_buggy"
    history_features_path_template = "SegundaGeracao/commons-compress/commons-compress_{}_buggy/history_features.csv"
    code_churns_path_template = "SegundaGeracao/commons-compress/commons-compress_{}_buggy/code_churns_features_multithread.csv"


    # Loop from 1 to 64
    for i in range(1, 48):
        repo_path = path_template.format(i)
        REPO_PATH = repo_path
        code_churns_path = code_churns_path_template.format(i)
        history_features_path = history_features_path_template.format(i)
        assemble_dataset(history_features_path, code_churns_path, REPO_PATH)

