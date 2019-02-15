#!/usr/bin/env python3

import itertools
import os
import random

from optparse import OptionParser

settings = {}


class Player(object):
    def __init__(self, name, team, team_pos, player_id):
        self.name = name
        self.team = team
        self.team_pos = team_pos
        self.player_id = player_id


class Table(object):
    def __init__(self, num, players=None):
        self.num = num
        if players is not None:
            self.players = players
        else:
            self.players = []


class Round(object):
    def __init__(self, num, tables=None):
        self.num = num
        if tables is not None:
            self.tables = tables
        else:
            self.tables = []


class Tournament(object):
    def __init__(self, rounds=None):
        if rounds is not None:
            self.rounds = rounds
        else:
            self.rounds = []

        self.reinit_stats()

    def reinit_stats(self):
        self.internal_team_intersections = 0
        self.max_num_team_intersections = 0
        self.max_num_player_intersections = 0

        self.team_intersections_matrix = [[0 for x in range(settings['NUM_TEAMS'])] for y in range(settings['NUM_TEAMS'])]
        self.player_intersections_matrix = [[0 for x in range(settings['NUM_PLAYERS'])] for y in range(settings['NUM_PLAYERS'])]

    def calculate_intersections(self):
        assert self.rounds
        assert self.players

        self.reinit_stats()

        for r in self.rounds:
            for t in r.tables:
                team_numbers = []
                player_numbers = []
                for p in t.players:
                    if p.team in team_numbers:
                        print("WARNING: Internal team intersection in round %u table %u with team %u" % (r.num, t.num, p.team))
                        self.internal_team_intersections += 1

                    team_numbers.append(p.team)
                    player_numbers.append(p.player_id)

                team_combinations = itertools.combinations(team_numbers, 2)
                for team_pair in team_combinations:
                    first = team_pair[0]
                    second = team_pair[1]
                    self.team_intersections_matrix[first - 1][second - 1] += 1
                    self.team_intersections_matrix[second - 1][first - 1] += 1

                player_combinations = itertools.combinations(player_numbers, 2)
                for player_pair in player_combinations:
                    first = player_pair[0]
                    second = player_pair[1]
                    self.player_intersections_matrix[first - 1][second - 1] += 1
                    self.player_intersections_matrix[second - 1][first - 1] += 1

        self.max_num_team_intersections = max(map(max, self.team_intersections_matrix))
        self.max_num_player_intersections = max(map(max, self.player_intersections_matrix))

        self.print_intersections_stats()

    def print_intersections_stats(self):
        print("")
        print("Team intersections matrix:")
        print('\n'.join([''.join(['{:4}'.format(item) for item in row]) for row in self.team_intersections_matrix]))

        # print("")
        # print("Player intersections matrix:")
        # print('\n'.join([''.join(['{:2}'.format(item) for item in row]) for row in self.player_intersections_matrix]))

        print("")
        print("Tournament intersection stats:")
        print("Internal: %u" % self.internal_team_intersections)
        print("Max number of team intersections: %u" % self.max_num_team_intersections)
        print("Max number of player intersections: %u" % self.max_num_player_intersections)

    # very simple and slow algorithm for now
    def remove_internal_intersections(self):
        iteration_number = 0

        while True:
            self.calculate_intersections()
            if self.internal_team_intersections == 0:
                print("Successfully removed internal intersections after %u iterations" % iteration_number)
                break

            if iteration_number == settings['MAX_ITERATIONS']:
                print("Limit of iterations reached, exiting algorithm")
                break

            print("")
            print("Iteration #%u" % iteration_number)

            # each round in independent in terms of internal intersections
            for r in self.rounds:
                team_players_by_table = [[0 for x in range(settings['NUM_TABLES_IN_ROUND'])] for y in range(settings['NUM_TEAMS'])]
                for t in r.tables:
                    for p in t.players:
                        team_players_by_table[p.team - 1][t.num - 1] += 1

                for team in range(0, settings['NUM_TEAMS']):
                    tables_without_this_team = [table for table in r.tables if team_players_by_table[team][table.num -1] == 0]

                    for table in r.tables:
                        if team_players_by_table[team][table.num - 1] < 2:
                            continue

                        players_from_this_team = [player for player in table.players if player.team == team + 1]

                        random_table = random.choice(tables_without_this_team)
                        random_this_player = random.choice(players_from_this_team)
                        random_other_player = random.choice(random_table.players)

                        table.players.remove(random_this_player)
                        table.players.append(random_other_player)

                        random_table.players.remove(random_other_player)
                        random_table.players.append(random_this_player)

            iteration_number += 1


def generate_tournament_from_text(text):
    tournament = Tournament()

    tournament.rounds = [Round(i + 1) for i in range(0, settings['NUM_ROUNDS'])]
    tournament.players = [Player('',
                                 (i) // 4 + 1,
                                 (i) % 4 + 1,
                                 i + 1) for i in range(0, settings['NUM_PLAYERS'])]

    rounds_text = text.splitlines()
    assert len(rounds_text) == settings['NUM_ROUNDS']
    round_num = 0

    for r in rounds_text:
        current_round = tournament.rounds[round_num]
        round_num += 1

        current_round.tables = [Table(i + 1) for i in range(0, settings['NUM_TABLES_IN_ROUND'])]

        tables_text = r.split()
        assert len(tables_text) == settings['NUM_TABLES_IN_ROUND']
        table_num = 0

        for t in tables_text:
            current_table = current_round.tables[table_num]
            table_num += 1

            players_ids_text = t.split('-')
            assert len(players_ids_text) == 4

            for p in players_ids_text:
                player_id = int(p)
                current_player = tournament.players[player_id - 1]
                current_table.players.append(current_player)

    return tournament


def generate_text_from_tournament(tournament):
    text = """"""
    for r in tournament.rounds:
        for t in r.tables:
            for p in t.players:
                text += str(p.player_id)
                if p != t.players[len(t.players) - 1]:
                    text += "-"
            if t != r.tables[len(r.tables) - 1]:
                text += " "
        text += "\n"

    return text


def main():
    parser = OptionParser()

    parser.add_option('-t', '--teams',
                      type='int',
                      help='Number of teams')

    parser.add_option('-i', '--iterations',
                      type='int',
                      help='Maximum number of iterations',
                      default=10)

    opts, _ = parser.parse_args()
    number_of_teams = opts.teams
    max_iterations = opts.iterations

    data_file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'initial_data',
        '{}_teams.txt'.format(number_of_teams)
    )

    if not os.path.exists(data_file_path):
        print("We don't have initial data for {} teams".format(number_of_teams))
        return

    with open(data_file_path, 'r') as f:
        seating_text = f.read()

    global settings
    settings = {
        'NUM_TEAMS': number_of_teams,
        'NUM_PLAYERS': number_of_teams * 4,
        'NUM_TABLES_IN_ROUND': number_of_teams,
        'NUM_ROUNDS': 7,
        'MAX_ITERATIONS': max_iterations
    }

    tournament = generate_tournament_from_text(seating_text)

    initial_seating = generate_text_from_tournament(tournament)
    print("Initial seating:")
    print(initial_seating)

    tournament.remove_internal_intersections()
    tournament.calculate_intersections()

    new_seating = generate_text_from_tournament(tournament)
    print("")
    print("New seating:")
    print(new_seating)


if __name__ == '__main__':
    main()
