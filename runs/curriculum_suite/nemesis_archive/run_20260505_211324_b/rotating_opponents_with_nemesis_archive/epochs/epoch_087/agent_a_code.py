def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = (0, 0)
    best_key = None
    # Heuristic: prioritize resources where we are relatively closer than opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        best_rel = None  # maximize opp_t - self_t
        best_self = None
        for rx, ry in res:
            self_t = man(nx, ny, rx, ry)
            opp_t = man(ox, oy, rx, ry)
            rel = opp_t - self_t
            key = (rel, -self_t)  # larger rel better; smaller self_t better
            if best_rel is None or key > (best_rel, best_self):
                best_rel = rel
                best_self = -self_t

        # Secondary: if tie, prefer moves that keep us closer to the overall nearest resource
        nearest_self = min(man(nx, ny, rx, ry) for rx, ry in res)
        tie_key = (best_rel, best_self, -nearest_self, -abs(nx - ox) - abs(ny - oy))
        if best_key is None or tie_key > best_key:
            best_key = tie_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]