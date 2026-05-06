def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position", None)
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not targets:
        best = None; bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d = dist((nx, ny), (ox, oy))
            if bestv is None or d < bestv:
                bestv = d; best = (dx, dy)
        return list(best if best is not None else (0, 0))

    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ns = (nx, ny)
        self_d = min(dist(ns, t) for t in targets)
        opp_d = min(dist((ox, oy), t) for t in targets)

        # Pick the best resource swing we can create this move.
        swing = -10**9
        for t in targets:
            ds = dist(ns, t)
            do = dist((ox, oy), t)
            # Positive means we get relatively closer than opponent.
            s = (do - ds) * 5 - ds
            if do <= ds:
                s += 3  # better contest
            swing = s if s > swing else swing

        # Secondary: if we can't swing contests, prefer reducing distance to opponent (intercept).
        intercept = -dist(ns, (ox, oy))
        # Tertiary: slight preference for closer overall resource.
        key = swing + 2 * (opp_d - self_d) + 0.5 * intercept - 0.1 * self_d
        scored.append((key, dx, dy))

    # Deterministic tie-break by (key desc, dx asc, dy asc)
    scored.sort(key=lambda x: (-x[0], x[1], x[2]))
    return [scored[0][1], scored[0][2]] if scored else [0, 0]