#! /usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict

import options
import sys

from .priority_queue import HardRulesQueue
from .rule_evaluator import RuleEval


class HardRulesEvaluator:
    def __init__(self, rules, task):
        self.rules = defaultdict(list)
        for rule in rules:
            print(rule)
            print(task.init)
            evaluator = RuleEval(rule, task)
            self.rules[evaluator.action_schema].append(evaluator)


class HardRulesMatchTree(HardRulesEvaluator):
    def __init__(self, rules, task):
        super(HardRulesMatchTree, self).__init__(rules, task)
        self.match_tree = {}
        for schema in self.rules:
            for target_schema in self.rules[schema]:
                if (not target_schema in self.match_tree):
                    self.match_tree[target_schema] = []
                for arg_ids in self.rules[schema][target_schema]:
                    self.match_tree[target_schema].append({})
    def print_info(self):
        print("Matchtree hard rules evaluator.")
    def _in_tree(self, args, index, subtree):
        if (index + 1 >= len(args)): # leaf node in tree
            return args[index] in subtree or "*" in subtree
        if (index < len(args)):
            if (args[index] in subtree):
                return self._in_tree(args, index + 1, subtree[args[index]])
            elif ("*" in subtree):
                return self._in_tree(args, index + 1, subtree["*"])
        return False
    def is_hard_action(self, action):
        if (action.predicate.name in self.match_tree):
            for i in range(len(self.match_tree[action.predicate.name])):
                if (self._in_tree(action.args, 0, self.match_tree[action.predicate.name][i])):
                    return True 
        return False
    def _add_entry(self, args, arg_ids, index, subtree):
        if (arg_ids[index] == -1):
            arg = "*"
        else:
            arg = args[arg_ids[index]]
        added = False
        if (not arg in subtree):
            added = True
            if (index + 1 >= len(arg_ids)):
                subtree.append(arg)
            elif (index + 2 >= len(arg_ids)):
                subtree[arg] = []
            else:
                subtree[arg] = {}
        if (index + 1 < len(arg_ids)):
            return self._add_entry(args, arg_ids, index + 1, subtree[arg])
        return added
    def notify_action(self, action):
        if (action.predicate.name in self.rules):
            added = set()
            for target_schema in self.rules[action.predicate.name]:
                for i in range(len(self.rules[action.predicate.name][target_schema])):
                    arg_ids = self.rules[action.predicate.name][target_schema][i]
                    if (self._add_entry(action.args, arg_ids, 0, self.match_tree[target_schema][i])):
                        added.add(target_schema) 
            return added
        return []
                
class HardRulesHashSet(HardRulesEvaluator):
    def __init__(self, rules, task):
        super(HardRulesHashSet, self).__init__(rules, task)

    def print_info(self):
        print("Hashset hard rules evaluator.")

    def is_hard_action(self, action):
        if (action.predicate.name in self.rules):
            for item in self.rules[action.predicate.name]:
                if item.evaluate(action) == 1:
                    return 1
        return False

    def notify_action(self, action):
        return []


def get_hard_rules_from_options(inner_queue, task):
    args = options.hard_rules
    
    type = args[0].lower()
    with open(args[1]) as f:
        rules = f.readlines()
    rules = [x.strip() for x in rules] 
 
    if (type == "hashset"):
        evaluator = HardRulesHashSet(rules, task)
    elif (type == "matchtree"):
        evaluator = HardRulesMatchTree(rules, task)
    else:
        sys.exit("Error: unknown hard-rule queue type: " + type)
        
    return HardRulesQueue(inner_queue, evaluator)
    
