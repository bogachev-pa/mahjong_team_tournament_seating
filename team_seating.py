#!/usr/bin/env python3

import itertools

NUM_TEAMS = 17
NUM_PLAYERS = NUM_TEAMS * 4
NUM_TABLES_IN_ROUND = NUM_PLAYERS // 4
NUM_ROUNDS = 7

seating_text = """8-15-17-68  3-16-19-60  29-35-50-59 26-33-62-65 1-10-45-66  13-21-22-38 28-43-58-61 20-40-44-57 36-39-63-67 4-42-46-64  9-23-41-49  30-53-55-56 2-11-34-54  6-12-18-52  27-47-48-51 25-31-32-37 5-7-14-24
5-6-55-59   35-37-53-62 3-15-47-67  17-20-29-43 1-26-49-61  18-32-38-51 21-31-34-48 27-46-58-60 8-28-45-65  9-10-36-57  14-22-40-42 19-56-64-68 7-11-23-66  4-12-54-63  24-44-50-52 13-33-39-41 2-16-25-30
48-60-62-67 20-21-49-65 8-24-40-63  28-35-44-47 13-42-57-58 4-27-34-59  2-29-33-52  17-36-37-38 11-12-19-61 50-54-66-68 7-16-45-46  10-18-55-64 6-41-43-56  22-39-51-53 5-26-30-32  14-15-23-31 1-3-9-25
14-38-58-64 46-52-56-61 2-13-20-62  8-9-33-34   23-35-40-67 1-5-16-18   24-42-60-65 4-10-26-53  21-47-59-68 7-17-32-48  31-41-55-66 15-25-27-49 12-50-51-57 22-43-45-63 6-37-44-54  19-29-30-39 3-11-28-36
24-28-34-66 3-17-26-44  9-39-48-61  8-58-59-62  15-37-43-51 6-23-30-65  18-49-67-68 2-19-41-63  7-20-38-53  16-31-54-64 32-42-45-56 5-22-50-60  25-35-55-57 29-36-46-47 10-27-40-52 4-11-13-14  1-12-21-33
26-31-36-40 7-9-15-59   1-34-42-68  16-22-24-55 5-20-63-64  33-46-54-67 12-14-17-39 21-35-61-66 2-3-18-56   27-43-44-65 11-32-49-62 19-25-38-52 6-28-51-60  37-48-50-58 8-47-53-57  4-30-41-45  10-13-23-29
1-11-29-57  5-34-44-67  10-56-63-65 18-19-31-45 3-24-30-54  8-37-49-60  2-47-64-66  9-43-52-68  6-15-33-61  7-40-55-58  20-22-32-59 4-28-39-62  23-46-50-53 16-17-42-51 35-38-41-48 14-21-27-36 12-13-25-26"""


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

        self.team_intersections_matrix = [[0 for x in range(NUM_TEAMS)] for y in range(NUM_TEAMS)]
        self.player_intersections_matrix = [[0 for x in range(NUM_PLAYERS)] for y in range(NUM_PLAYERS)]

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

        print("")
        print("Team intersections matrix:")
        print('\n'.join([''.join(['{:4}'.format(item) for item in row]) for row in self.team_intersections_matrix]))

        print("")
        print("Player intersections matrix:")
        print('\n'.join([''.join(['{:2}'.format(item) for item in row]) for row in self.player_intersections_matrix]))

        print("")
        print("Tournament intersection stats:")
        print("Internal: %u" % self.internal_team_intersections)
        print("Max number of team intersections: %u" % self.max_num_team_intersections)
        print("Max number of player intersections: %u" % self.max_num_player_intersections)


def generate_tournament_from_text(text):
    tournament = Tournament()

    tournament.rounds = [Round(i + 1) for i in range(0, NUM_ROUNDS)]
    tournament.players = [Player('',
                                 (i) // 4 + 1,
                                 (i) % 4 + 1,
                                 i + 1) for i in range(0, NUM_PLAYERS)]

    rounds_text = seating_text.splitlines()
    assert len(rounds_text) == NUM_ROUNDS
    round_num = 0

    for r in rounds_text:
        current_round = tournament.rounds[round_num]
        round_num += 1

        current_round.tables = [Table(i + 1) for i in range(0, NUM_TABLES_IN_ROUND)]

        tables_text = r.split()
        assert len(tables_text) == NUM_TABLES_IN_ROUND
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
    tournament = generate_tournament_from_text(seating_text)

    new_text = generate_text_from_tournament(tournament)
    print(new_text)

    tournament.calculate_intersections()

if __name__ == '__main__':
    main()
