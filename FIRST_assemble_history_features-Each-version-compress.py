"""
Script to extract history features from a git repository.
"""
__author__ = "Oscar Svensson"
__copyright__ = "Copyright (c) 2018 Axis Communications AB"
__license__ = "MIT"

import csv
import json
import os
import time

from argparse import ArgumentParser
from datetime import datetime
import collections

from pygit2 import Repository, GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE
from tqdm import tqdm


def set_to_list(obj):
    """
    Helper function to convert a set to a list.
    """
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


def get_files_in_tree(tree, repo):
    """
    Extract the hex of all files and their name.
    """
    files = set()
    for entry in tree:
        if entry.type == "tree":
            sub_files = [(f[0], "{}/{}".format(entry.name, f[1]))
                         for f in get_files_in_tree(repo[entry.id], repo)]
            files.update(sub_files)
        else:
            blob = repo[entry.id]
            if (hasattr(blob, 'is_binary')) and (not blob.is_binary):
                if entry.name.endswith("java"):
                    files.add((entry.hex, entry.name))
    return files


def get_diffing_files(commit, parent, repo):
    """
    Get the files that diffed between two commits.
    """
    diff = repo.diff(parent, commit)

    patches = [p for p in diff]

    files = set()

    for patch in patches:
        if patch.delta.is_binary:
            continue
        nfile = patch.delta.new_file
        files.add((nfile.id, nfile.path, patch.delta.status))

    return files


def save_history_features_graph(repo_path, branch, graph_path_file, graph_path):
    """
    Track the number of developers that have worked in a repository and save the
    results in a graph which could be used for later use.
    """
    repo = Repository(repo_path)
    head = repo.references.get(branch)

    commits = list(
        repo.walk(head.target, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE))
    current_commit = repo.head.target

    start_time = time.time()

    all_files = {}
    current_commit = repo.get(str(current_commit))
    files = get_files_in_tree(current_commit.tree, repo)

    for (_, name) in tqdm(files):
        all_files[name] = {}
        all_files[name]['lastcommit'] = current_commit.hex
        all_files[name][current_commit.hex] = {}
        all_files[name][current_commit.hex]["prevcommit"] = ""
        all_files[name][current_commit.hex]["authors"] = [
            current_commit.committer.name
        ]

    for i, commit in enumerate(tqdm(commits[1:])):
        files = get_diffing_files(commit, commits[i], repo)
        for (_, name, _) in files:
            if name not in all_files:
                all_files[name] = {}

            last_commit = ""
            if 'lastcommit' not in all_files[name]:
                all_files[name]['lastcommit'] = commit.hex
            else:
                last_commit = all_files[name]['lastcommit']

            all_files[name][commit.hex] = {}
            all_files[name][commit.hex]["prevcommit"] = last_commit

            authors = set([commit.committer.name])
            if last_commit and ("authors" in all_files[name][commit.hex]):
                authors.update(all_files[name][last_commit]["authors"])
            all_files[name][commit.hex]["authors"] = authors

            all_files[name]['lastcommit'] = commit.hex

    if not os.path.exists(graph_path):
        os.makedirs(graph_path, mode=0o777)

    with open(graph_path_file, 'w') as output:
        json.dump(all_files, output, default=set_to_list)

    end_time = time.time()

    print("Done")
    print("Overall processing time {}".format(end_time - start_time))


def load_history_features_graph(path):
    """
    Save the history features to a csv file.
    """
    file_graph = {}
    with open(path, 'r') as inp:
        file_graph = json.load(inp)
    return file_graph


def get_history_features(graph, repo_path, branch):
    """
    Function that extracts the history features from a git repository.
    They are the total number of authors, the total age and the total
    number of unique changes.
    """
    repo = Repository(repo_path)
    head = repo.references.get(branch)

    commits = list(
        repo.walk(head.target, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE))

    features = []
    commit_features_by_file = [str(commits[0].hex), str(commits[0].hex), str(1.0), str(0.0), str(0.0)]
    features.append(commit_features_by_file)
    name_author = dict()
    commits_until_now = dict()
    commit_timestamp = dict()

    for i, commit in enumerate(tqdm(commits[1:])):
        files = get_diffing_files(commit, commits[i], repo)

        for (_, name, _) in files:
            sub_graph = graph[name][commit.hex]

            if name not in name_author:
                name_author[name] = [sub_graph['authors'][0]]
            else:
                authorsList = name_author[name]
                if sub_graph['authors'][0] not in authorsList:
                    authorsList.append(sub_graph['authors'][0])
                    name_author[name] = authorsList

            if name not in commits_until_now:
                commits_until_now[name] = [commit.hex]
            else:
                commitList = commits_until_now[name]
                if commit.hex not in commitList:
                    commitList.append(commit.hex)
                    commits_until_now[name] = commitList

            total_number_of_authors = len(name_author[name])
            total_number_of_changes = len(commits_until_now[name])

            total_age = 0

            commit_features_by_file = []

            prev_commit = sub_graph['prevcommit']
            if prev_commit:
                prev_commit_obj = repo.get(prev_commit)
                commmitDateTime = datetime.utcfromtimestamp(commit.commit_time)
                prevcommitDateTime = datetime.utcfromtimestamp(prev_commit_obj.commit_time)
                total_age = int((commmitDateTime - prevcommitDateTime).total_seconds() / 60)

            if total_age >= 0:
                commit_features_by_file.append(name)
                commit_features_by_file.append(str(commit.hex))
                commit_features_by_file.append(total_number_of_authors)
                commit_features_by_file.append(total_age)
                commit_features_by_file.append(total_number_of_changes)
                features.append(commit_features_by_file)
                total_number_of_authors = 0
                commit_timestamp[commit.hex] = datetime.utcfromtimestamp(commit.commit_time)

    save_commit_timestamps(commit_timestamp, repo_path + "/commit_timestamps.csv")
    return features


def save_history_features(history_features, path):
    """
    Function to save the history features as a csv file.
    """
    with open(path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            ["name", "commit", "number_of_authors", "age", "number_unique_changes"])
        for row in history_features:
            if row:
                if not str(row[0]).endswith(".java"):
                    continue
                writer.writerow([row[0], row[1], row[2], row[3], row[4]])

def save_commit_timestamps(history_features, path):
    """
    Function to save the history features as a csv file.
    """
    with open(path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            ["commit", "timestamp"])
        for k, v in history_features.items():
            writer.writerow([k, v])



if __name__ == "__main__":


	# Path template to be formatted with numbers from 1 to 64
    path_template = "TerceiraGeracao/commons-compress/commons-compress_{}_buggy"
    graph_path_and_file = "TerceiraGeracao/commons-compress/commons-compress_{}_buggy/file_graph.json"
    graph_path = "TerceiraGeracao/commons-compress/commons-compress_{}_buggy"
    output_path = "TerceiraGeracao/commons-compress/commons-compress_{}_buggy/history_features.csv"
    branch = "HEAD"

    # Loop from 1 to 64
    for i in range(1, 48):
        # Format the repository path with the current number
        repo_path = path_template.format(i)
        REPO_PATH = repo_path
        BRANCH = branch
        GRAPH_PATH_FILE = graph_path_and_file.format(i)
        GRAPH_PATH = graph_path.format(i)
        OUTPUT = output_path.format(i)
        save_history_features_graph(REPO_PATH, BRANCH, GRAPH_PATH_FILE, GRAPH_PATH)
        GRAPH = load_history_features_graph(GRAPH_PATH_FILE)
        HISTORY_FEATURES = get_history_features(GRAPH, REPO_PATH, BRANCH)
        save_history_features(HISTORY_FEATURES, OUTPUT)




    
