def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(0, 0)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            cand.append((dx, dy))

    if resources:
        res_list = [tuple(p) for p in resources]
    else:
        res_list = []

    best = ( -10**18, 0, 0)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        if res_list:
            best_res = 10**18
            for rx, ry in res_list:
                d = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                if d < best_res:
                    best_res = d
            dist_res = best_res
        else:
            dist_res = 0

        dist_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        # Prefer minimizing distance to nearest resource; tie-break toward maximizing separation from opponent.
        score = (-dist_res) * 1000 + dist_opp
        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]