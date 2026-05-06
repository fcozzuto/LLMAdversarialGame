def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if (sx, sy) in set((r[0], r[1]) for r in resources):
        return [0, 0]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx*dx + dy*dy

    if not resources:
        # Deterministic fallback: head to center while moving away from opponent.
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        target = (tx, ty)
    else:
        # Target a resource where we are (relatively) closer than the opponent.
        best = None
        for r in resources:
            rx, ry = r[0], r[1]
            ds = dist2((sx, sy), (rx, ry))
            do = dist2((ox, oy), (rx, ry))
            key = (ds - do, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        target = best[1]

    best_move = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer getting closer to target; also prefer increasing distance from opponent.
        dt = dist2((nx, ny), target)
        dpo = dist2((nx, ny), (ox, oy))
        # Tie-break deterministically by delta order.
        key = (dt, -dpo, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]