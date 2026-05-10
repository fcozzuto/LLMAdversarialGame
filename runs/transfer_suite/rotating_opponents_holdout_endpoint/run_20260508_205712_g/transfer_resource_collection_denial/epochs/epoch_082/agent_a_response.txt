def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                res.append((x, y))

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if valid(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    if not res:
        cx, cy = (W - 1) // 2, (H - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - cx) + abs(ny - cy)
            cand = (d, nx, ny, dx, dy)
            if best is None or cand < best:
                best = cand
        return [int(best[3]), int(best[4])]

    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # immediate capture bonus if resource on target cell
        on_res = 1 if (nx, ny) in set(res) else 0

        # evaluate best resource we can contest (prefer where we are closer)
        best_local = -10**9
        for tx, ty in res:
            myd = abs(nx - tx) + abs(ny - ty)
            opd = abs(ox - tx) + abs(oy - ty)
            # Prefer targets where we are closer; also prefer closer overall; discourage letting opponent get there first.
            val = (10 if myd == 0 else 0) + (opd - myd) * 2 - myd
            if val > best_local:
                best_local = val

        # slight preference for reducing distance to opponent to deny paths, without fully chasing
        opp_dist = abs(nx - ox) + abs(ny - oy)
        score = on_res * 100 + best_local - opp_dist * 0.02

        cand = (-score, dx, dy)  # deterministic tie-break: smaller dx then dy after score
        if best_score is None or cand < best_score:
            best_score = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]