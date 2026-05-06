def choose_move(observation):
    sx, sy = observation["self_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources", [])
    edge = [cell for cell in resources if cell[0] in (0, w - 1) or cell[1] in (0, h - 1)]
    if edge:
        target = min(edge, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
    else:
        if sy == 0 and sx < w - 1:
            return [1, 0]
        if sx == w - 1 and sy < h - 1:
            return [0, 1]
        if sy == h - 1 and sx > 0:
            return [-1, 0]
        if sx == 0 and sy > 0:
            return [0, -1]
        target = [0, 0]
    dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
    dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
    return [dx, dy]