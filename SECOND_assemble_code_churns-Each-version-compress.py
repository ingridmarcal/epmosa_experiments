"""
Script to extract code churns.
"""
__author__ = "Oscar Svensson"
__copyright__ = "Copyright (c) 2018 Axis Communications AB"
__license__ = "MIT"

import csv
import math
import os
import sys
import time

from argparse import ArgumentParser

from multiprocessing import Process, Manager, cpu_count
from pygit2 import Repository, GIT_SORT_REVERSE, GIT_SORT_TOPOLOGICAL
from tqdm import tqdm


# Global variables


def parse_code_churns(RES, pid, repo_path, branch, start, stop=-1):
    """
    Function that is intended to be runned by a process. It extracts the code churns
    for a set of commits and stores them in the RES dict.
    """
    repo = Repository(repo_path)

    head = repo.references.get(branch)
    commits = list(
        repo.walk(head.target, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE))

    start = start - 1 if (start > 0) else start
    commits = commits[start:stop] if (stop != -1) else commits[start:]

    code_churns = [[] for c in range(len(commits))]
    files_stats = dict()

    accumulated_number_of_changes = 0
    for i, commit in enumerate(tqdm(commits[1:], position=pid)):
        diff = repo.diff(commits[i], commit)

        # usar a árvore para considerar somente
        tree = commit.tree
        patches = [p for p in diff]

        # Count the total lines of code and find the biggest file that have been changed
        total_tloc = 0
        line_of_code_old = 0

        for patch in patches:
            if patch.delta.is_binary:
                continue
            new_file = patch.delta.new_file
            new_file_name = new_file.path

            #todo verificar se a condição é suficiente para pegar somente .java files que não são teste.
            if not str(new_file_name).endswith(".java"):
                continue

            # Total lines of code
            total_tloc += get_file_lines_of_code(repo, tree, new_file)

            old_file = patch.delta.old_file
            # Total lines of code in the old file
            line_of_code_old = max(
                line_of_code_old, get_file_lines_of_code(repo, tree, old_file))

            class_stats = []

            class_stats.append(str(new_file_name))
            class_stats.append(str(commit.hex))
            class_stats.append(get_file_lines_of_code(repo, tree, new_file)) #new size
            class_stats.append(str(patch.line_stats[1]))  # lines added to the file
            class_stats.append(str(patch.line_stats[2]))  # lines removed to the file

            code_churns[i].append(class_stats)


    RES[pid] = code_churns


def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier + 0.5) / multiplier


def count_files(tree, repo):
    """
    Count how many files there are in a repository.
    """
    num_files = 0
    trees = []
    visited = set()
    visited.add(tree.id)
    trees.append(tree)

    while trees:
        current_tree = trees.pop()
        for entry in current_tree:
            if entry.type == "tree":
                if entry.id not in visited:
                    trees.append(repo[entry.id])
                    visited.add(entry.id)
            else:
                num_files += 1
    return num_files


def get_file_lines_of_code(repo, tree, dfile):
    """
    Count how many lines of code there are in a file.
    """
    tloc = 0
    try:
        blob = repo[tree[dfile.path].id]

        tloc = len(str(blob.data).split('\\n'))
    except Exception as _:
        return tloc
    return tloc


def get_file_name(repo, tree, dfile):
    name = ""
    try:
        blob = repo[tree[dfile.path].id]
        name = blob.name
    except Exception as _:
        return name
    return name


def get_code_churns(repo_path, branch, RES):
    """
    General function for extracting code churns. It first extracts the code churns for
    the first commit and then starts a number of processes(equal to the number of cores
    on the computer), which equally extracts the code churns for the remaining commits.
    """
    repo = Repository(repo_path)

    head = repo.references.get(branch)

    commits = list(
        repo.walk(head.target, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE))
    code_churns = [[]]

    initial = commits[0]

    # Check how many processes that could be spawned
    cpus = cpu_count()
    print("Using {} cpus...".format(cpus))

    # Equally split the commit set into the equally sized parts.
    quote, remainder = divmod(len(commits), cpus)

    processes = [
        Process(
            target=parse_code_churns,
            args=(RES, i, repo_path, branch, i * quote + min(i, remainder),
                  (i + 1) * quote + min(i + 1, remainder))) for i in range(cpus)
    ]

    for process in processes:
        process.start()

    start_time = time.time()
    for process in processes:
        process.join()
    end_time = time.time()

    print("Done")
    print("Overall processing time {}".format(end_time - start_time))

    # Assemble the results
    churns = []
    for _, churn in RES.items():
        churns.extend(churn)

    churns = list(reversed(churns))
    return churns


def save_churns(churns, path):
    """
    Saves the code churns to a csv file.
    """

    # definir formato explicitamente? UTF-8
    with open(path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([
            "file_name", "commit", "size", "lines_of_code_added", "lines_of_code_deleted"
        ])

        for row in churns:
            if row:
                for file in row:
                    writer.writerow([file[0], file[1], file[2], file[3], file[4]])





if __name__ == "__main__":

    # Path template to be formatted with numbers from 1 to 64
    path_template = "TerceiraGeracao/commons-compress/commons-compress_{}_buggy"
    graph_path_and_file = "TerceiraGeracao/commons-compress/commons-compress_{}_buggy/file_graph.json"
    graph_path = "TerceiraGeracao/commons-compress/commons-compress_{}_buggy"
    output_path = "TerceiraGeracao/commons-compress/commons-compress_{}_buggy/code_churns_features_multithread.csv"
    branch = "HEAD"

    with Manager() as manager:

        # Loop from 1 to 64
                
        for i in range(1, 48):
            # Format the repository path with the current number
            repo_path = path_template.format(i)
            REPO_PATH = repo_path
            BRANCH = branch
            GRAPH_PATH_FILE = graph_path_and_file.format(i)
            GRAPH_PATH = graph_path.format(i)
            OUTPUT = output_path.format(i)
            if not os.path.exists(REPO_PATH):
                print("The repository path does not exist!")
                sys.exit(1)

            RES = manager.dict()
            CHURNS = get_code_churns(REPO_PATH, BRANCH, RES)
            save_churns(CHURNS, OUTPUT)
