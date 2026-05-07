def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def md(x1, y1, x2, y2):
        ax = x1 - x2
        ay = y1 - y2
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    # Opponent likely targets their nearest resource; we bias toward resources we can beat.
    opp_best = min(res, key=lambda t: md(ox, oy, t[0], t[1]))
    best_margin = -10**18
    best = (0, 0)

    def edge_bias(x, y):
        dx = x if x < (gw - 1 - x) else (gw - 1 - x)
        dy = y if y < (gh - 1 - y) else (gh - 1 - y)
        return dx + dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate this step by the best resource where we are ahead (opp_dist - self_dist).
        local_best = -10**18
        for rx, ry in res:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            margin = od - sd  # positive => we are closer/equal than opponent
            # If we can't beat anyone, still prefer reducing our distance to resources far from opponent.
            if margin >= 0:
                val = margin * 100 - sd - 0.5 * edge_bias(nx, ny)
            else:
                val = (-margin) * 0.2 - sd - 0.03 * edge_bias(nx, ny) - (md(nx, ny, opp_best[0], opp_best[1]) * 0.01)
            if val > local_best:
                local_best = val

        # If multiple moves tie, deterministically prefer smaller lexicographic delta.
        if local_best > best_margin or (local_best == best_margin and (dx, dy) < best):
            best_margin = local_best
            best = (dx, dy)

    return [int(best[0]), int(best[1])]