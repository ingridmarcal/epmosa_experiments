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


def get_commit_pairs():
    # Python program to read
    # json file

    import json

    # Opening JSON file
    f = open("current_repos/commons-compress/fix_introducers_Compress.json")

    # returns JSON object as
    # a dictionary
    data = json.load(f)

    # Closing file
    f.close()
    return data


def get_timestamps():
    timestamps = dict()

    with open("current_repos/commons-compress/commit_timestamps.csv") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if row:
                timestamps[row[0]] = row[1]

    # datetime_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')
    return timestamps


def assemble_commit_labels(REPO_PATH):
    timestamps = get_timestamps()
    pairs = get_commit_pairs()
    dataset = []
    appender = 0

    with open("current_repos/commons-compress/all_features.csv") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if not row or row[0] == "name":
                continue
            for pair in pairs:
                if row[1] == pair[0]:
                    appender = 0
                else:
                    if row[1] == pair[1]:
                        appender = 1
                    else:
                        if is_buggy(row[1], timestamps, pair[0], pair[1]):
                            appender = 1
                        else:
                            continue
            row.append(appender)
            dataset.append(row)

    save_to_csv(dataset)


def is_buggy(commit, timestamps, introducer, fixer):

    #todo é suficiente para garantir que a classe é buggy?

    if introducer in timestamps.keys() and fixer in timestamps.keys() and commit in timestamps.keys():
        i_timestamp = datetime.strptime(timestamps[introducer], '%Y-%m-%d %H:%M:%S')
        f_timestamp = datetime.strptime(timestamps[fixer], '%Y-%m-%d %H:%M:%S')
        if timestamps[commit] != "timestamp":
            c_timestamp = datetime.strptime(timestamps[commit], '%Y-%m-%d %H:%M:%S')

            #todo porém a classe deve ter sido mexida no introducer.
            if i_timestamp <= c_timestamp <= f_timestamp:
                return True
            else:
                return False
        else:
            return False
    else:
        return False



def save_to_csv(features):
    """
    Function to save the history features as a csv file.
    """
    with open("current_repos/commons-compress/dataset.csv", 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            ["name", "commit", "number_of_authors", "age", "number_unique_changes", "size", "lines_added",
             "lines_deleted", "buggy"])
        for row in features:
            if row:
                writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]])

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
    REPO_PATH = "current_repos/commons-compress"
    history_features_path = "current_repos/commons-compress/history_features.csv"
    code_churns_path = "current_repos/commons-compress/code_churns_features_multithread.csv"

    # Loop from 1 to 64
    for i in range(1, 2):
        # Format the repository path with the current number
        assemble_dataset(history_features_path, code_churns_path, REPO_PATH)
        print("")
        assemble_commit_labels(REPO_PATH)


    #assemble_dataset() #1
    #assemble_commit_labels() #2 Só para quando for gerar dataset para treino
