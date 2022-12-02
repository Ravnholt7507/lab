#! /usr/bin/env python
# -*- coding: utf-8 -*-

import options

from collections import defaultdict
import heapq
import sys
import timers

from random import randint


class PriorityQueue():
    def __init__(self):
        fail
    def get_final_queue(self):
        pass
    def get_num_grounded_actions(self):
        pass
    def get_num_actions(self):
        pass
    def print_stats(self):
        print("no statistics available")

class FIFOQueue(PriorityQueue):
    def __init__(self):
        self.queue = []
        self.queue_pos = 0
        self.last_hard_index = 0
        self.hard_actions = []
    def __bool__(self):
        return self.queue_pos < len(self.queue)
    __nonzero__ = __bool__
    def get_final_queue(self):
        return self.queue[:self.queue_pos] + self.hard_actions
    def print_info(self):
        print("Using FIFO priority queue for actions.")
    def get_num_grounded_actions(self):
        return self.queue_pos + len(self.hard_actions)
    def get_num_actions(self):
        return len(self.queue) + len(self.hard_actions)
    def get_hard_action_if_exists(self, is_hard_action):
        if (self.last_hard_index < self.queue_pos):
            self.last_hard_index = self.queue_pos
        for i in range(self.last_hard_index, len(self.queue)):
            action = self.queue[i]
            if (is_hard_action(action)):
                self.hard_actions.append(action)
                del self.queue[i]
                return [action]
            self.last_hard_index += 1
        return []
    def notify_new_hard_actions(self, schemas):
        self.last_hard_index = self.queue_pos
    def push(self, action):
        self.queue.append(action)
    def pop(self):
        result = self.queue[self.queue_pos]
        self.queue_pos += 1
        return result

class LIFOQueue(PriorityQueue):
    def __init__(self):
        self.queue = []
        self.closed = []
        self.last_hard_index = 0
    def __bool__(self):
        return len(self.queue) > 0
    __nonzero__ = __bool__
    def get_final_queue(self):
        return self.closed
    def print_info(self):
        print("Using LIFO priority queue for actions.")
    def get_num_grounded_actions(self):
        return len(self.closed)
    def get_num_actions(self):
        return len(self.queue) + len(self.closed)
    def get_hard_action_if_exists(self, is_hard_action):
        for i in range(self.last_hard_index, len(self.queue)):
            action = self.queue[i]
            if (is_hard_action(action)):
                self.closed.append(action)
                del self.queue[i]
                return [action]
            self.last_hard_index += 1
        return []
    def notify_new_hard_actions(self, schemas):
        self.last_hard_index = 0
    def push(self, action):
        self.queue.append(action)
    def pop(self):
        result = self.queue.pop()
        if (self.last_hard_index >= len(self.queue)):
            self.last_hard_index = max(0, len(self.queue) - 1)
        self.closed.append(result)
        return result


class SortedHeapQueue():
    def __init__(self, min_wins = True):
        self.queue = []
        self.count = 0 # this speeds up the queue significantly
        self.min_wins = min_wins # if true, return minimal element, if false return maximal
    def __bool__(self):
        return bool(self.queue)
    __nonzero__ = __bool__
    def get_hard_action_if_exists(self, is_hard_action):
#         return [action for estimate, action in self.queue if is_hard_action(action)]
# did not help too much + can even have negative impact on runtime
# probably try this as a parameter n; where each call returns up to n hard actions
        for i in range(len(self.queue)):
            action = self.queue[i][1]
            if (is_hard_action(action)):
                del self.queue[i]
                heapq.heapify(self.queue)
                return [action]
        return []
    def notify_new_hard_actions(self):
        pass
    def push(self, action, estimate):
        if (self.min_wins):
            heapq.heappush(self.queue, (estimate, self.count, action))
        else:
            heapq.heappush(self.queue, (-estimate, self.count, action))
        self.count += 1
    def push_list(self, actions, estimates):
        assert(len(actions) == len(estimates))
        for i in range(len(actions)):
            if (self.min_wins):
                heapq.heappush(self.queue, (estimates[i], self.count, actions[i]))
            else:
                heapq.heappush(self.queue, (-estimates[i], self.count, actions[i]))
            self.count += 1
    def pop(self):
        return heapq.heappop(self.queue)[2]
    def pop_entry(self):
        if (self.min_wins):
            return (heapq.heappop(self.queue)[0], heapq.heappop(self.queue)[2])
        else:
            return (-heapq.heappop(self.queue)[0], heapq.heappop(self.queue)[2])

class RandomEvaluator():
    def get_estimate(self, action):
        return randint(0, 10)
    def print_stats(self):
        pass

class NoveltyEvaluator():
    def __init__(self):
        self.novelty = {}
    def calculate_novelty(self, action):
        if (not action.predicate.name in self.novelty):
            return 0
        else:
            novelty = sys.maxsize if len(action.args) > 0 else 0 # action without arguments are always novel; no blow-up here
            for i in range(len(action.args)):
                if (action.args[i] in self.novelty[action.predicate.name][i]):
                    novelty = min(novelty, self.novelty[action.predicate.name][i][action.args[i]])
                else:
                    return 0
            return novelty
    def update_novelty(self, action):
        if (not action.predicate.name in self.novelty):
            self.novelty[action.predicate.name] = [{} for i in range(len(action.args))]
            for i in range(len(action.args)):
                self.novelty[action.predicate.name][i][action.args[i]] = 1
        else:
            for i in range(len(action.args)):
                if (action.args[i] in self.novelty[action.predicate.name][i]):
                    self.novelty[action.predicate.name][i][action.args[i]] += 1
                else:
                    self.novelty[action.predicate.name][i][action.args[i]] = 1



class ActionsFromFileQueue(PriorityQueue):
    def __init__(self):
        if (not options.actions_file):
            sys.error("need to provide --actionsfile FILE for ActionsFromFileQueue")
        self.actions = defaultdict(set)
        with open(options.actions_file[0], 'r') as afile:
            for action in afile:
                if (action.startswith(";")):
                    # this is probably the "; cost = X (unit cost)" part of a plan file
                    continue
                action = action.replace("(", "").replace(")", "").strip()
                schema, args = action.split(" ", 1)
                schema.strip()
                args.strip()
                args = "".join([x.strip() for x in args.split(" ")])
                self.actions[schema].add(args)
        self.queue = []
        self.not_in_file = []
        self.closed = []
    def __bool__(self):
        while (self.queue):
            result = self.queue[-1]
            schema = result.predicate.name
            args = "".join(result.args)
            if (args in self.actions[schema]):
                return True
            self.not_in_file.append(result)
            self.queue.pop()
        if (options.reachable_actions_output_file): # at this point the grounding is done; somewhat ugly, though
            print("Writing all actions that became reachable during grounding to ", options.reachable_actions_output_file[0])
            with open(options.reachable_actions_output_file[0], 'w') as outfile:
                for action in self.closed + self.not_in_file:
                    outfile.write("{} {}\n".format(action.predicate.name, " ".join(action.args)))
        return False
    __nonzero__ = __bool__
    def get_final_queue(self):
        return self.closed
    def print_info(self):
        print("Using ActionsFromFile priority queue for actions.")
    def get_num_grounded_actions(self):
        return len(self.closed)
    def get_num_actions(self):
        return len(self.queue) + len(self.closed)
    def get_hard_action_if_exists(self, is_hard_action):
        fail("not supported by ActionsFromFileQueue")
    def notify_new_hard_actions(self, schemas):
        fail("not supported by ActionsFromFileQueue")
    def push(self, action):
        self.queue.append(action)
    def pop(self):
        while (self):
            result = self.queue.pop()
            schema = result.predicate.name
            args = "".join(result.args)
            if (args in self.actions[schema]):
                self.closed.append(result)
                return result
            self.not_in_file.append(result)

class EvaluatorQueue(PriorityQueue):
    def __init__(self, evaluator, info):
        self.queue = SortedHeapQueue(False)
        self.closed = []
        self.model = evaluator
        self.info = info
        self.batch_eval = options.batch_evaluation
        self.non_evaluated_actions = defaultdict(list)
    def __bool__(self):
        return bool(self.queue) or (self.batch_eval and any(bool(actions) for actions in self.non_evaluated_actions.values()))
    __nonzero__ = __bool__
    def get_final_queue(self):
        return self.closed
    def print_info(self):
        print("Using heap priority queue with a trained model for actions.")
        if (self.batch_eval):
            print("Actions are evaluated in batches.")
        print(self.info)
    def print_stats(self):
        self.model.print_stats()
    def get_hard_action_if_exists(self, is_hard_action):
        # TODO support for batch evaluation
        actions = self.queue.get_hard_action_if_exists(is_hard_action)
        if (actions):
            self.closed += actions
        return actions
    def notify_new_hard_actions(self, schemas):
        self.queue.notify_new_hard_actions(schemas)
    def push(self, action):
        if (self.batch_eval):
            self.non_evaluated_actions[action.predicate.name].append(action)
        else:
            estimate = self.model.get_estimate(action)
            if (estimate == None):
                estimate = randint(0, 100) / 100 # TODO not sure if this is really a good idea
            self.queue.push(action, estimate)
    def pop(self):
        if (self.batch_eval and any(bool(l) for l in self.non_evaluated_actions.values())):
            for schema, actions in self.non_evaluated_actions.items():
                if (actions):
                    estimates = self.model.get_estimates(actions)
                    if not estimates:
                        # we have no model for this action schema
                        estimates = [randint(0, 100) / 100 for i in range(len(actions))] # TODO not sure if this is really a good idea
                    self.queue.push_list(actions, estimates)
                    self.non_evaluated_actions[schema] = []
        action = self.queue.pop()
        self.closed.append(action)
        return action


class TrainedQueue(PriorityQueue):
    def __init__(self, task):
        from subdominization.model import TrainedModel
        if (not options.trained_model_folder):
            sys.exit("Error: need trained model to use this queue. Please specify using --trained-model-folder")
        if (not task):
            sys.exit("Error: no task given")
        self.queue = SortedHeapQueue()
        self.closed = []
#         self.sorted_closed = []
#         self.pop_count = 0
        timer = timers.Timer()
        self.model = TrainedModel(options.trained_model_folder, task)
        self.loading_time = str(timer)
    def __bool__(self):
        return bool(self.queue)
    __nonzero__ = __bool__
    def get_final_queue(self):
        return self.closed
    def print_info(self):
        print("Using heap priority queue with a trained model for actions.")
        print("Loaded trained model from", options.trained_model_folder, self.loading_time)
    def print_stats(self):
        self.model.print_stats()
#         while(len(self.sorted_closed) > 0):
#             item = heapq.heappop(self.sorted_closed)
#             print(round(1 - item[0], 2), item[1], "(" + str(item[2].predicate.name), end=" ")
#             print(item[2].args[0], end="")
#             for arg in item[2].args[1:]:
#                 print(" " + arg, end="")
#             print(")")
    def push(self, action):
        estimate = self.model.get_estimate(action)
        if (estimate == None):
            estimate = randint(0, 100) / 100
        self.queue.push(action, 1 - estimate)
    def pop(self):
        action = self.queue.pop()
        self.closed.append(action)
#         heapq.heappush(self.sorted_closed, (result[0], self.pop_count, result[1]))
#         self.pop_count += 1
        return action

class AlephQueue(TrainedQueue):
    def __init__(self, task):
        from subdominization.rule_evaluator_aleph import RuleEvaluatorAleph
        if (not options.aleph_model_file):
            sys.exit("Error: need trained model to use this queue. Please specify using --aleph-model-file")
        if (not task):
            sys.exit("Error: no task given")
        self.queue = SortedHeapQueue()
        self.closed = []
        timer = timers.Timer()
        with open(options.aleph_model_file, "r") as aleph_rules:
            self.model = RuleEvaluatorAleph(aleph_rules.readlines(), task)
        self.loading_time = str(timer)
    def print_info(self):
        print("Using heap priority queue with a trained aleph model for actions.")
        print("Loaded trained model from", options.aleph_model_file, self.loading_time)

class SchemaRoundRobinQueue(PriorityQueue):
    def __init__(self):
        self.schemas = []
        self.current = 0
        self.queues = []
        self.num_grounded_actions = []
    def __bool__(self):
        for queue in self.queues:
            if (queue):
                return True
        return False
    __nonzero__ = __bool__
    def get_final_queue(self):
        result = []
        for queue in self.queues:
            result += queue.get_final_queue()
        return result
    def print_info(self):
        print("Using SchemaRoundRobin priority queue for actions.")
    def print_stats(self):
        for i in range(len(self.num_grounded_actions)):
            print("%d actions grounded for schema %s" % (self.num_grounded_actions[i], self.schemas[i]))
    def get_hard_action_if_exists(self, is_hard_action):
        for i in range(len(self.queues)):
            action = self.queues[i].get_hard_action_if_exists(is_hard_action)
            if (action):
                self.num_grounded_actions[i] += 1
                return [action]
        return []
    def notify_new_hard_actions(self, schemas):
        for schema in schemas:
            if (schema in self.schemas):
                self.queues[self.queues.index(schema)].notify_new_hard_actions(schemas)
    def push(self, action):
        if (not action.predicate.name in self.schemas):
            self.schemas.append(action.predicate.name)
            self.queues.append(FIFOQueue())
            self.num_grounded_actions.append(0)
        self.queues[self.schemas.index(action.predicate.name)].push(action)
    def pop(self):
        while True:
            self.current = (self.current + 1) % len(self.schemas)
            if (self.queues[self.current]):
                self.num_grounded_actions[self.current] += 1
                return self.queues[self.current].pop()


class NoveltyFIFOQueue(PriorityQueue):
    def __init__(self):
        self.novel_action_queue = []
        self.novel_queue_pos = 0
        self.novel_last_hard_index = 0
        self.closed_novel_actions = []
        self.non_novel_action_queue = FIFOQueue()
        self.num_novel_actions_grounded = 0
        self.num_non_novel_actions_grounded = 0
        self.novelty = NoveltyEvaluator()
    def __bool__(self):
        if (self.novel_queue_pos < len(self.novel_action_queue)):
            return True
        if (self.non_novel_action_queue):
            return True
        return False
    __nonzero__ = __bool__
    def get_final_queue(self):
        return self.non_novel_action_queue.get_final_queue() + self.closed_novel_actions
    def print_info(self):
        print("Using novelty FIFO priority queue for actions.")
    def print_stats(self):
        print("Grounded %d novel actions" % self.num_novel_actions_grounded)
        print("Grounded %d non-novel actions" % self.num_non_novel_actions_grounded)
    def get_hard_action_if_exists(self, is_hard_action):
        if (self.novel_last_hard_index < self.novel_queue_pos):
            self.novel_last_hard_index = self.novel_queue_pos
        for i in range(self.novel_last_hard_index, len(self.novel_action_queue)):
            action = self.novel_action_queue[i]
            if (is_hard_action(action)):
                self.closed_novel_actions.append(action)
                self.num_novel_actions_grounded += 1
                del self.novel_action_queue[i]
                return [action]
            self.novel_last_hard_index += 1
        hard_actions = self.non_novel_action_queue.get_hard_action_if_exists(is_hard_action)
        if (hard_actions):
            self.num_non_novel_actions_grounded += len(hard_actions)
        return hard_actions
    def notify_new_hard_actions(self, schemas):
        self.non_novel_action_queue.notify_new_hard_actions(schemas)
        self.novel_last_hard_index = self.novel_queue_pos
    def push(self, action):
        if (self.novelty.calculate_novelty(action) == 0):
            self.novel_action_queue.append(action)
        else:
            self.non_novel_action_queue.push(action)
    def pop(self):
        while (self.novel_queue_pos < len(self.novel_action_queue)):
            action = self.novel_action_queue[self.novel_queue_pos]
            self.novel_queue_pos += 1
            if (self.novelty.calculate_novelty(action) == 0):
                self.novelty.update_novelty(action)
                self.num_novel_actions_grounded += 1
                self.closed_novel_actions.append(action)
                return action
            else:
                self.non_novel_action_queue.push(action)
        # removed all actions from novel queue
        assert(self.novel_queue_pos >= len(self.novel_action_queue))
        action = self.non_novel_action_queue.pop()
        self.num_non_novel_actions_grounded += 1
        return action

class RoundRobinNoveltyQueue(PriorityQueue):
    def __init__(self):
        self.novelty = NoveltyEvaluator()
        self.schemas = []
        self.current = 0
        self.queues = []
        self.num_grounded_actions = []
        self.closed = []
        self.hard_closed = defaultdict(list)
    def __bool__(self):
        for queue in self.queues:
            if (queue):
                return True
        return False
    __nonzero__ = __bool__
    def get_final_queue(self):
        res = self.closed
        for list in self.hard_closed.values():
            res += list
        return res
    def print_info(self):
        print("Using round-robin novelty priority queue for actions.")
    def print_stats(self):
        for i in range(len(self.num_grounded_actions)):
            print("%d actions grounded for schema %s" % (self.num_grounded_actions[i], self.schemas[i]))
    def get_hard_action_if_exists(self, is_hard_action):
        for i in range(len(self.queues)):
            actions = self.queues[i].get_hard_action_if_exists(is_hard_action)
            res = []
            if (len(actions) > 0):
                for action in actions:
                    if (not action in self.hard_closed[action.predicate.name]):
                        res.append(action)
                        self.hard_closed[action.predicate.name].append(action)
                        self.num_grounded_actions[i] += 1
                return res
        return []
    def notify_new_hard_actions(self, schemas):
        for queue in self.queues:
            queue.notify_new_hard_actions()
    def push(self, action):
        novelty = self.novelty.calculate_novelty(action)
        if (not action.predicate.name in self.schemas):
            self.schemas.append(action.predicate.name)
            self.queues.append(SortedHeapQueue())
            self.num_grounded_actions.append(0)
        self.queues[self.schemas.index(action.predicate.name)].push(action, novelty)

    def pop(self):
        while True:
            self.current = (self.current + 1) % len(self.schemas)
            while (self.queues[self.current]):
                novelty_old, action = self.queues[self.current].pop_entry()
                if (action in self.hard_closed[action.predicate.name]):
                    continue
                if (novelty_old == 0):
                    novelty_new = self.novelty.calculate_novelty(action)
                    if (novelty_new != novelty_old):
                        self.queues[self.current].push(action, novelty_new)
                        continue
                        self.novelty.update_novelty(action)
                        self.closed.append(action)
                self.num_grounded_actions[self.current] += 1
        return action

class RoundRobinTrainedQueue(PriorityQueue):
    def __init__(self, task):
        from subdominization.model import TrainedModel
        if (not options.trained_model_folder):
            sys.exit("Error: need trained model to use this queue. Please specify using --trained-mode-folder")
        if (not task):
            sys.exit("Error: no task given")
        timer = timers.Timer()
        self.model = TrainedModel(options.trained_model_folder, task)
        self.loading_time = str(timer)
        self.schemas = []
        self.current = 0
        self.queues = []
        self.num_grounded_actions = []
        self.closed = []
    def __bool__(self):
        for queue in self.queues:
            if (queue):
                return True
        return False
    __nonzero__ = __bool__
    def get_final_queue(self):
        return self.closed
    def print_info(self):
        print("Using trained round-robin priority queue for actions.")
        print("Loaded trained model from", options.trained_model_folder, self.loading_time)
    def print_stats(self):
        self.model.print_stats()
        for i in range(len(self.num_grounded_actions)):
            print("%d actions grounded for schema %s" % (self.num_grounded_actions[i], self.schemas[i]))
    def get_hard_action_if_exists(self, is_hard_action):
        # TODO support for batch evaluation
        for i in range(len(self.queues)):
            action = self.queues[i].get_hard_action_if_exists(is_hard_action)
            if (action):
                self.has_actions = False
                self.closed.append(action)
                self.num_grounded_actions[i] += 1
                if (self.queues[i]):
                    self.has_actions = True
                else:
                    self.__check_has_action()
                return action
        return None
    def notify_new_hard_actions(self):
        for queue in self.queues:
            queue.notify_new_hard_actions()
    def push(self, action):
        estimate = self.model.get_estimate(action)
        if (not action.predicate.name in self.schemas):
            self.schemas.append(action.predicate.name)
            self.num_grounded_actions.append(0)
            if (estimate != None):
                self.queues.append(SortedHeapQueue())
            else:
                self.queues.append(FIFOQueue())
        if (estimate != None):
            self.queues[self.schemas.index(action.predicate.name)].push(action, 1 - estimate)
        else:
            self.queues[self.schemas.index(action.predicate.name)].push(action)
    def pop(self):
        while True:
            self.current = (self.current + 1) % len(self.schemas)
            if (self.queues[self.current]):
                self.num_grounded_actions[self.current] += 1
                action = self.queues[self.current].pop()
                self.closed.append(action)
                return action

class RoundRobinAlephQueue(RoundRobinTrainedQueue):
    def __init__(self, task):
        from subdominization.rule_evaluator_aleph import RuleEvaluatorAleph
        if (not options.aleph_model_file):
            sys.exit("Error: need trained model to use this queue. Please specify using --aleph-model-file")
        if (not task):
            sys.exit("Error: no task given")
        timer = timers.Timer()
        with open(options.aleph_model_file, "r") as aleph_rules:
            self.model = RuleEvaluatorAleph(aleph_rules.readlines(), task)
        self.loading_time = str(timer)
        self.schemas = []
        self.current = 0
        self.queues = []
        self.num_grounded_actions = []
        self.closed = []
    def print_info(self):
        print("Using trained round-robin aleph priority queue for actions.")
        print("Loaded trained model from", options.trained_model_folder, self.loading_time)


class HardRulesQueue(PriorityQueue):
    def __init__(self, inner_queue, hard_rules_evaluator):
        self.queue = inner_queue
        self.evaluator = hard_rules_evaluator
        self.num_hard_rule_actions = 0
        self.tmp_hard_actions = []
    def __bool__(self):
        return bool(self.queue)
    __nonzero__ = __bool__
    def get_final_queue(self):
        return self.queue.get_final_queue()
    def print_info(self):
        print("Using hard-rule priority queue for actions with the following inner queue and hard-rule evaluator:")
        self.queue.print_info()
        self.evaluator.print_info()
    def print_stats(self):
        print("Number actions from hard rules:", self.num_hard_rule_actions)
        self.queue.print_stats()
    def push(self, action):
        self.queue.push(action)
    def pop(self):
        if (len(self.tmp_hard_actions) == 0):
            self.tmp_hard_actions = self.queue.get_hard_action_if_exists(self.evaluator.is_hard_action)
        if (len(self.tmp_hard_actions) > 0):
            ground_action = self.tmp_hard_actions.pop()
            self.num_hard_rule_actions += 1
        else:
            ground_action = self.queue.pop()
        target_schemas = self.evaluator.notify_action(ground_action)
        if (len(target_schemas) > 0):
            self.queue.notify_new_hard_actions(target_schemas)
        return ground_action


def get_action_queue_from_options(task = None):
    name = options.grounding_action_queue_ordering.lower()
    if (name == "fifo"):
        return FIFOQueue()
    elif (name == "lifo"):
        return LIFOQueue()
    elif (name == "random"):
        return EvaluatorQueue(RandomEvaluator(), f"Using random action priority.")
    elif (name == "trained"):
        return TrainedQueue(task)
    elif (name == "roundrobintrained"):
        return RoundRobinTrainedQueue(task)
    elif (name == "aleph"):
        return AlephQueue(task)
    elif (name == "roundrobinaleph"):
        return RoundRobinAlephQueue(task)
    elif (name == "roundrobin"):
        return SchemaRoundRobinQueue()
    elif (name == "noveltyfifo"):
        return NoveltyFIFOQueue()
    elif (name == "roundrobinnovelty"):
        return RoundRobinNoveltyQueue()
    else:
        sys.exit("Error: unknown queue type: " + name)
