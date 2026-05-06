def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not res:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            key = (dist(nx, ny, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Interception heuristic: prefer next moves that get us closer than the opponent to some resource,
    # especially when the opponent is relatively closer.
    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        best_adv = None
        best_self = None
        best_opp = None
        for rx, ry in res:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # advantage: positive means we are closer than opponent (in Manhattan steps)
            adv = od - sd
            if best_adv is None or (adv, -sd, -od, -rx, -ry) > best_adv:
                best_adv = (adv, -sd, -od, -rx, -ry)
                best_self = sd
                best_opp = od

        # Global key: maximize advantage, then minimize our distance, then move deterministically
        # Tie-break pushes toward blocking by also preferring positions far from opponent when equal.
        adv_val = best_adv[0]
        key = (-adv_val, best_self, dist(nx, ny, ox, oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]