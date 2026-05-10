def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    best = None
    # Phase 1: secure a resource we are at least as close to as the opponent.
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        if ds <= do:
            key = (-(do - ds), ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))

    # Phase 2: if none, contest the resource closest to opponent (resource denier).
    if best is None:
        for rx, ry in resources:
            do = man(ox, oy, rx, ry)
            ds = man(sx, sy, rx, ry)
            key = (do, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))

    tx, ty = best[1]
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-breaker order already in deltas.
    best_move = (10**9, 10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = man(nx, ny, tx, ty)
        # Secondary safety: don't move onto cells that are closer to opponent than ours by too much.
        opp_dist = man(nx, ny, tx, ty)  # equal since same target; keep deterministic simple
        key = (dist, 0, dx, dy)
        if key < best_move:
            best_move = key

    return [best_move[2], best_move[3]]