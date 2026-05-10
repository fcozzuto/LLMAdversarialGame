def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []

    obs = set((p[0], p[1]) for p in obstacles if len(p) >= 2)
    targets = [(c[0], c[1]) for c in unclaimed if len(c) >= 2]
    if not targets:
        targets = [(w // 2, h // 2)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_sc = -10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        # Pick a single best target deterministically by a combined metric.
        best_t_sc = 10**18
        for tx, ty in targets[:20]:
            dm = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            # Prefer reducing our distance while keeping opponent farther.
            t_sc = dm - (do * 0.2)
            if t_sc < best_t_sc:
                best_t_sc = t_sc
        # Higher is better; tie-break deterministically by move order.
        sc = -best_t_sc
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]