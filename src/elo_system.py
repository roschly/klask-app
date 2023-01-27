class ELOSystem:
    def __init__(self, players):
        self.players = {player: {"elo": 1500, "matches": 0} for player in players}

    def _calc_k_factor(self, player):
        n = self.players[player]["matches"]
        k_factor = 0.5 + 0.5 * (1 - 1.1 ** (-n))
        return 50 * k_factor

    def add_player(self, name):
        assert name not in self.players.keys()
        self.players[name] = {"elo": 1500, "matches": 0}

    def get_elo(self, name):
        return self.players[name]["elo"]

    def update_elo(self, name, elo_change):
        self.players[name]["elo"] += elo_change
        self.players[name]["matches"] += 1

    def calc_expectation(self, player1, player2):
        r1 = self.get_elo(player1)
        r2 = self.get_elo(player2)
        return 1 / (1 + 10 ** ((r2 - r1) / 400))

    def new_match(self, winner, loser):
        exp = self.calc_expectation(winner, loser)

        k_winner = self._calc_k_factor(winner)
        k_loser = self._calc_k_factor(loser)
        k_factor = min(k_winner, k_loser)

        self.update_elo(winner, (1 - exp) * k_factor)
        self.update_elo(loser, (exp - 1) * k_factor)
