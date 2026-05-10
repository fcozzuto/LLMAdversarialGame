def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if unclaimed:
        targets = unclaimed
    else:
        targets = list(opp_t) if opp_t else [(sx, sy)]

    # Prefer unclaimed closer to center but also close to us; deterministic tie-breaks.
    best_score = None
    best_t = (sx, sy)
    for tx, ty in targets:
        d = abs(tx - sx) + abs(ty - sy)
        dc = abs(tx - cx) + abs(ty - cy)
        do = abs(tx - ox) + abs(ty - oy)
        # Lower is better: keep distance short, contest center, slightly avoid opponent proximity.
        score = (d, dc, -do, ty, tx)
        if best_score is None or score < best_score:
            best_score, best_t = score, (tx, ty)

    tx, ty = best_t

    def move_score(nx, ny):
        if (nx, ny) in obstacles:
            return (10**9, 10**9, 10**9, 0, 0)
        # Prefer reducing distance to target; prefer capturing by moving into opponent territory.
        d1 = abs(tx - nx) + abs(ty - ny)
        cap_opp = 0 if (nx, ny) in opp_t else 1  # entering opp_t is better => smaller cap_opp
        # Also prefer expanding at frontier: moving adjacent to our territory.
        adj = 0
        for ax, ay in ((1,0),(-1,0),(0,1),(0,-1)):
            if (nx+ax, ny+ay) in self_t:
                adj = 1
                break
        # Deterministic bias to keep progress: slight penalty for staying.
        stay_pen = 1 if (nx == sx and ny == sy) else 0
        return (d1, cap_opp, -adj, stay_pen, ny, nx)

    best_move = (0, 0)
    best_ms = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        ms = move_score(nx, ny)
        if best_ms is None or ms < best_ms:
            best_ms = ms
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]