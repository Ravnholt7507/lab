#!/usr/bin/env python3
import os
import platform

from downward import suites
from downward.experiment import FastDownwardExperiment
from downward.reports.absolute import AbsoluteReport
from lab.environments import LocalEnvironment, BaselSlurmEnvironment
from lab.experiment import Experiment
from lab.reports import Attribute, geometric_mean
import shutil


# Create custom report class with new attributes.
class MyReport(AbsoluteReport):
    INFO_ATTRIBUTES = ["time_limit", "memory_limit", "total_time", "total_memory"]
    ERROR_ATTRIBUTES = ["domain", "problem", "algorithm", "unexplained_errors", "error", "node"]

NODE = platform.node()
#BENCHMARKS_DIR = "/Users/andreasravnholt/Universitet/5semester/planners/downward-projects/benchmarks"
BENCHMARKS_DIR = "/Users/andreasravnholt/Universitet/5semester/planners/usefull/depots/runs/optimal"
REPO = "/Users/andreasravnholt/Universitet/5semester/lab"
REV = "main"
ENV = LocalEnvironment(processes=2)

SUITES = ["depot"]
ATTRIBUTES = ["error", "plan", "times", Attribute("coverage", absolute=True, min_wins=False, scale="linear")]
TIME_LIMIT = 1800
MEMORY_LIMIT = 2048

#Create the experiment
exp = FastDownwardExperiment(environment=ENV)
#add custom parser for ff
exp.add_parser("fast-downward.py")
exp.add_algorithm(
    "blind",
    REPO,
    REV,
    ["--translate-options", "--grounding-action-queue-ordering", "fifo",
     "--termination-condition", "goal-relaxed-reachable", "min-number", "745", "--search-options", "--search",
     "eager_greedy([ff])"],
)
for task in suites.build_suite(BENCHMARKS_DIR, SUITES):
    run = exp.add_run()
    run.add_resource("domain", task.domain_file, symlink=True)
    run.add_resource("problem", task.problem_file, symlink=True)
    run.set_property("domain", task.domain)
    run.set_property("problem", task.problem)
    run.set_property("algorithm", "ff")
    run.set_property("time_limit", TIME_LIMIT)
    run.set_property("memory_limit", MEMORY_LIMIT)
    run.set_property("id", ["ff", task.domain, task.problem])

exp.add_step("build", exp.build)
exp.add_step("start", exp.start_runs)
exp.add_fetcher(name="fetch")
exp.add_report(MyReport(attributes=ATTRIBUTES), outfile="report.html")
exp.run_steps()
