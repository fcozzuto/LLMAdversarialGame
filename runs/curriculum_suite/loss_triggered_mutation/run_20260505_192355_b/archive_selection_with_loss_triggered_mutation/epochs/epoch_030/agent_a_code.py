def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not res:
        # Move toward center deterministically
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            dist = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            key = (dist, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # New policy: pick move that maximizes "win margin" on the best available resource,
    # using opponent distance as a direct competitive signal.
    best_key = None
    best_move = (0, 0)
    # Tie-break order: prefer staying out of obstacles but deterministic via lexicographic.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # Evaluate only a small deterministic subset of resources: closest to us now.
        # (Keeps it fast and deterministic without full search.)
        scored = []
        for rx, ry in res:
            d0 = man(sx, sy, rx, ry)
            scored.append((d0, rx, ry))
        scored.sort()
        subset = scored[: min(6, len(scored))]
        best_margin = None
        best_self_dist = None
        for _, rx, ry in subset:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Margin: bigger means we are closer than opponent (at this moment).
            margin = opp_d - self_d
            # Also mildly penalize absolute self distance to actually secure resources.
            self_eff = self_d
            key_local = (margin, -self_eff, -rx, -ry)
            if best_margin is None or key_local > best_margin:
                best_margin = key_local
                best_self_dist = self_d
        # Global key: maximize best_margin, then prefer smaller self distance, then lexicographic.
        key = (best_margin[0], best_margin[1], -best_self_dist, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]