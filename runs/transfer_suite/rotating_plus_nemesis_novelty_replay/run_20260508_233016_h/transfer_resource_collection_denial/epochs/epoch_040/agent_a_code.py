def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources]

    # If close to any resource, prioritize collecting it directly.
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        myd_list = [man(nx, ny, rx, ry) for rx, ry in res]
        opd_list = [man(ox, oy, rx, ry) for rx, ry in res]

        # Target score: win resource races; prefer moves that also reduce opponent's best opportunities.
        # Also add obstacle-proximity penalty to avoid "sticking" behind blockers.
        best_m = 10**9
        best_margin = -10**9
        best_idx = 0
        for i, (rx, ry) in enumerate(res):
            myd = myd_list[i]
            opd = opd_list[i]
            if myd < best_m:
                best_m = myd
                best_idx = i
            # Prefer cells where we are closer (myd <= opd) and significantly so.
            margin = opd - myd
            if margin > best_margin:
                best_margin = margin
                best_idx = i

        rx, ry = res[best_idx]

        # Tie-break toward moving closer to chosen target, but keep it deterministic.
        progress = -man(nx, ny, rx, ry)

        # Opponent interference: discourage stepping into opponent's likely next direction
        # relative to its nearest resource.
        # (Simple deterministic prediction: opponent moves toward its nearest resource.)
        opp_res = res[0]
        opp_best = 10**9
        for r in res:
            d = man(ox, oy, r[0], r[1])
            if d < opp_best:
                opp_best = d
                opp_res = r
        tx, ty = opp_res
        odx = 0 if tx == ox else (1 if tx > ox else -1)
        ody = 0 if ty == oy else (1 if ty > oy else -1)
        block_pen = 0
        if (nx, ny) == (ox + odx, oy + ody):
            block_pen = -3.0

        # Obstacle proximity: penalize if next move is adjacent to an obstacle cluster (helps avoid repeated hits).
        adj = 0
        for ox2, oy2 in obstacles:
            if man(nx, ny, ox2, oy2) == 1:
                adj += 1
        obst_pen = -1.0 * adj

        # In late game, be more decisive about grabbing the nearest reachable resource.
        late = 1.0 if turns_remaining is not None and turns_remaining <= 8 else 0.0
        haste = -best_m
        winrace = best_margin

        key = (-(winrace + 0.25 * haste * (1.0 + late)) + progress + obst_pen + block_pen, man(sx, sy, rx, ry), dx, dy)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)

    # If all moves invalid, stay still.
    try:
        return [int(best_move[0]), int(best_move[1])]
    except:
        return [0, 0]