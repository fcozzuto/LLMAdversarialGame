def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    width = observation["grid_width"]
    height = observation["grid_height"]
    phase = observation.get("turn_index", 0) % 4
    targets = [
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1],
        [0, 0],
    ]
    target = targets[phase]
    if abs(target[0] - ox) + abs(target[1] - oy) < abs(sx - ox) + abs(sy - oy):
        target = max(targets, key=lambda item: abs(item[0] - ox) + abs(item[1] - oy))
    dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
    dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
    return [dx, dy]