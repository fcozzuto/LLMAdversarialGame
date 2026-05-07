def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    legal = []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_set.add((p[0], p[1]))

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Choose resource we can likely reach first; deterministic.
    best_r = None
    best_s = -10**18
    for rx, ry in res:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # Prefer winning races (ds < do), then close by, then far from opponent.
        s = (do - ds) * 100 - ds + (do - ds > 0) * 20
        # Tie-break: prefer upper/left deterministically
        s += -0.001 * (rx + ry)
        if s > best_s:
            best_s = s
            best_r = (rx, ry)

    rx, ry = best_r if best_r is not None else res[0]

    # Pick move that heads to target; if race uncertain, also keep distance from opponent.
    best_move = (0, 0)
    best_v = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_to = md(nx, ny, rx, ry)
        d_opp = md(nx, ny, ox, oy)
        # If stepping onto opponent-closer cell, penalize.
        v = -d_to * 5 + d_opp
        # Strongly reward moving onto the target if possible.
        if (nx, ny) == (rx, ry):
            v += 10**6
        if v > best_v:
            best_v = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]