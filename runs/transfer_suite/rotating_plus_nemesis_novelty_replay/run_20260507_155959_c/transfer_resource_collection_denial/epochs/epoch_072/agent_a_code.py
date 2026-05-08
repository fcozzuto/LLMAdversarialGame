def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    env = observation.get("environment_name", "resource_collection")

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res_set = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res_set.add((x, y))

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (nx, ny) == (sx, sy) or (inb(nx, ny) and (nx, ny) not in obs):
                valid.append((dx, dy))
    valid.sort()

    if not res_set or env != "resource_collection":
        tx, ty = w // 2, h // 2
        best = (10**9, 10**9, 0, 0)
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - tx) + abs(ny - ty)
            if (d, abs(dx) + abs(dy), dx, dy) < best:
                best = (d, abs(dx) + abs(dy), dx, dy)
        return [best[2], best[3]]

    best_move = None
    best_score = 10**18
    # Race heuristic: prefer moves that maximize lead over opponent for the best resource,
    # with a small preference for nearer captures.
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # If move is invalid, engine keeps in place; but we only listed valid moves or stay.
        if (nx, ny) not in res_set:
            move_bonus = 0
        else:
            move_bonus = -100000  # deterministic strong bias to capture immediately

        min_race = None
        min_dist = None
        for rx, ry in res_set:
            myd = abs(nx - rx) + abs(ny - ry)
            opd = abs(ox - rx) + abs(oy - ry)
            race = myd - opd  # smaller is better (ahead)
            if min_race is None or (race, myd, rx, ry) < (min_race, min_dist, 0, 0):
                min_race = race
                min_dist = myd

        score = (min_race * 10) + min_dist + move_bonus
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]