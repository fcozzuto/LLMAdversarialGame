def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    ox, oy = observation["opponent_position"]

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_count(nx, ny, sset):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in sset:
                    c += 1
        return c

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        t = (nx, ny)
        a_self = adj_count(nx, ny, self_t)
        a_opp = adj_count(nx, ny, opp_t)
        dist_self_op = abs(nx - ox) + abs(ny - oy)
        score = 0

        if t in self_t:
            score += 2 + a_self - a_opp
        elif t in opp_t:
            score += 10 + 2 * a_self - 2 * a_opp
        elif t in unclaimed:
            score += 5 + 2 * a_self - 3 * a_opp

        edge = (nx in (0, w - 1)) or (ny in (0, h - 1))
        score += 1 if edge else 0

        # Deterministic tie-break: prefer moves that reduce distance to opponent
        score += -0.01 * dist_self_op

        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move