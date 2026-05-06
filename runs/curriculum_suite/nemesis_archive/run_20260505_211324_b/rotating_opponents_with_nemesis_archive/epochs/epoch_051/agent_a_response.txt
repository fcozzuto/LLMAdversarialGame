def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def on_edge(x, y):
        return x == 0 or y == 0 or x == w - 1 or y == h - 1

    # Target selection: avoid "edge race" if opponent is near/using edges.
    opp_edge_bias = 1 if on_edge(ox, oy) else 0
    best_target = None
    best_val = -10**18
    for tx, ty in res:
        myd = md(sx, sy, tx, ty)
        opd = md(ox, oy, tx, ty)
        lead = opd - myd  # positive means we reach earlier
        edge_pen = (2 if opp_edge_bias and on_edge(tx, ty) else 0)
        near_edge_bonus = (1 if (not on_edge(tx, ty) and opp_edge_bias) else 0)
        value = lead * 10 - myd + near_edge_bonus - edge_pen
        # tie-break deterministically
        if value > best_val or (value == best_val and (tx, ty) < best_target):
            best_val = value
            best_target = (tx, ty)
    tx, ty = best_target

    # Move choice: evaluate local neighbor cells with a slight "intercept" incentive against opponent's closest resource.
    local = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                local.append((dx, dy, nx, ny))
    if not local:
        return [0, 0]

    opp_target = min(res, key=lambda p: (md(ox, oy, p[0], p[1]), p[0], p[1]))

    best_move = None
    best_score = -10**18
    for dx, dy, nx, ny in local:
        myd = md(nx, ny, tx, ty)
        opd = md(ox, oy, tx, ty)
        gain = (opd - myd) * 10 - myd

        # Intercept: discourage letting opponent get too close to its own nearest resource.
        o_myd = md(nx, ny, opp_target[0], opp_target[1])
        o_opd = md(ox, oy, opp_target[0], opp_target[1])
        intercept = (o_opd - o_myd)  # higher means we can contest sooner

        # Small preference to reduce distance to chosen target.
        score = gain + intercept * 2 - 0.01 * (dx * dx + dy * dy)
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]