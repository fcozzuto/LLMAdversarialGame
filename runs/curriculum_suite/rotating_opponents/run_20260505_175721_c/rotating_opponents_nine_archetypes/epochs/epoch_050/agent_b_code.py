def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    near_self = [cell for cell in resources if abs(cell[0] - sx) + abs(cell[1] - sy) <= abs(cell[0] - ox) + abs(cell[1] - oy)]
    target = min((near_self or resources), key=lambda item: (abs(item[0] - sx) + abs(item[1] - sy), abs(item[0] - ox) + abs(item[1] - oy)))
    dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
    dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
    return [dx, dy]