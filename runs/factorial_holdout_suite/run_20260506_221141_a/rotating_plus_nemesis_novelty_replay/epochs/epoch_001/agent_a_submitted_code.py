def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles", [])
    obs = set(obstacles)
    resources = observation.get("resources", [])

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    has_res = bool(resources)

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue

        if has_res:
            dmin = None
            for rx, ry in resources:
                d = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                if dmin is None or d < dmin:
                    dmin = d
            do = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            score = -dmin + 0.02 * (-do)  # prefer being closer to resources; slight preference to reduce opponent distance
        else:
            score = -((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]