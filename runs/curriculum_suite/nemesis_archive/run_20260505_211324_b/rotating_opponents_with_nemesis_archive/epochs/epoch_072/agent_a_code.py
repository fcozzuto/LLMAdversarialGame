def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if not resources:
        best = None
        for dx, dy, nx, ny in moves:
            score = md(nx, ny, cx, cy) - 0.5 * md(nx, ny, ox, oy)
            if best is None or score < best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
                best = (score, dx, dy)
        return [best[1], best[2]]

    res_list = []
    for i, r in enumerate(resources):
        if isinstance(r, (list, tuple)) and len(r) == 2:
            rx, ry = r[0], r[1]
            if isinstance(rx, int) and isinstance(ry, int):
                res_list.append((rx, ry, i))
    if not res_list:
        best = None
        for dx, dy, nx, ny in moves:
            score = md(nx, ny, cx, cy) - 0.5 * md(nx, ny, ox, oy)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Pick a target resource that we can reach sooner than opponent, else least-bad
    def target_score(rx, ry):
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # Encourage "win" on access; discourage race where opponent is closer
        return ds - 0.9 * do + 0.05 * (rx + ry)

    best_move = None
    best_val = None
    for dx, dy, nx, ny in moves:
        val = md(nx, ny, cx, cy) * 0.02  # slight centering preference
        # Evaluate best target from this move
        move_best = None
        for rx, ry, _ in res_list:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            # If opponent is closer, add penalty; if close to a resource, add small bonus
            race_pen = 2.5 if do + 1 < ds else 0.0
            near_bonus = -0.15 * (1.0 / (1 + ds))
            t = ds - 0.9 * do + race_pen + near_bonus + 0.01 * (rx + ry)
            if move_best is None or t < move_best:
                move_best = t
        val += move_best

        # If standing next to opponent, back off slightly (resource_denier tends to contest)
        opp_dist = md(nx, ny, ox, oy)
        if opp_dist <= 1:
            val += 1.5 - 0.5 * opp_dist

        if best_val is None or val < best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]