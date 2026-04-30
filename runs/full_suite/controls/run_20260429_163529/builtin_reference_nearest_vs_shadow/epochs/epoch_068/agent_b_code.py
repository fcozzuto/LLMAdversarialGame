def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    def score(cell):
        self_d = abs(cell[0] - sx) + abs(cell[1] - sy)
        opp_d = abs(cell[0] - ox) + abs(cell[1] - oy)
        return (self_d - opp_d, self_d)
    target = min(resources, key=score)
    dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
    dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
    return [dx, dy]