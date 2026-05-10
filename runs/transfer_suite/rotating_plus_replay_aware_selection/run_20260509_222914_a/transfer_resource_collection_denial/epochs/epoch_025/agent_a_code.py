def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    res = []
    resset = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = p[0], p[1]
            res.append((rx, ry))
            resset.add((rx, ry))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            d = md(nx, ny, tx, ty)
            if best is None or d < best[0] or (d == best[0] and (nx, ny) < best[1]):
                best = (d, (nx, ny))
        return [best[1][0] - x, best[1][1] - y] if best else [0, 0]

    # Pick a target resource that we can reach earlier (deterministic).
    best_target = None
    best_key = None
    for rx, ry in res:
        ds = md(x, y, rx, ry)
        do = md(ox, oy, rx, ry)
        # Advantage: higher is better; tie-break by smaller self distance, then lexicographic.
        key = (do - ds, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        # Collect is best, otherwise maximize advantage relative to opponent.
        collected = 1 if (nx, ny) in resset else 0
        ns = md(nx, ny, tx, ty)
        no = md(ox, oy, tx, ty)
        # Encourage moving toward target and away from opponent's progress.
        # Add penalty for increasing distance to nearest resource cell we stand on next.
        nearest_res_dist = None
        for rx, ry in res:
            d = md(nx, ny, rx, ry)
            if nearest_res_dist is None or d < nearest_res_dist:
                nearest_res_dist = d
        if nearest_res_dist is None:
            nearest_res_dist = 0

        val = collected * 10_000 + (no - ns) * 50 - ns * 2 - nearest_res_dist
        if best_val is None or val > best_val:
            best_val = val
            best_move = (nx, ny)
        elif val == best_val and (best_move is None or (nx, ny) < best_move):
            best_move = (nx, ny)

    return [best_move[0] - x, best_move[1] - y] if best_move else [0, 0]