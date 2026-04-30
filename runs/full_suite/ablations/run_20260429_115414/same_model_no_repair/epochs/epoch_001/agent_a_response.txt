def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    blocked = obstacles
    def dist(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev for diagonal moves
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h: 
                continue
            if (nx, ny) in blocked: 
                continue
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None; bestv = None
        for dx, dy, nx, ny in candidates:
            dv = dist((nx, ny), (cx, cy)) + (0 if (nx, ny) != (ox, oy) else 0.5)
            if bestv is None or dv < bestv or (dv == bestv and (dx, dy) < best):
                bestv = dv; best = (dx, dy)
        return [best[0], best[1]]
    # Pick target resource where we are relatively closer than opponent.
    best_target = None; best_key = None
    for r in resources:
        tr = tuple(r)
        if tr in blocked: 
            continue
        our_d = dist((sx, sy), tr)
        opp_d = dist((ox, oy), tr)
        # maximize advantage; tie-break by smaller our distance
        key = (opp_d - our_d, -our_d, -tr[0], -tr[1])
        if best_key is None or key > best_key:
            best_key = key; best_target = tr
    tx, ty = best_target
    best_move = (0, 0); best_val = None
    for dx, dy, nx, ny in candidates:
        our_d = dist((nx, ny), (tx, ty))
        opp_d = dist((ox, oy), (tx, ty))
        # Prefer reducing our distance to target and avoid being on opponent.
        val = (our_d, -opp_d, 0 if (nx, ny) != (ox, oy) else 999)
        # Also slightly bias away from obstacles already handled; deterministic tie-break by (dx,dy)
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]