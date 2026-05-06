def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Heuristic: go for nearest resource while discouraging staying on interception lines.
    best = None
    best_score = -10**18
    for dx, dy, nx, ny in moves:
        # Resource value
        if resources:
            dmin = 10**9
            for rx, ry in resources:
                d = md(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d
            res_score = 10.0 / (1 + dmin)
        else:
            res_score = 0.0

        # Opponent pressure
        do = md(nx, ny, ox, oy)
        opp_score = 2.5 * (do / 10.0)

        # Break sweep/line interception: penalize if sharing row/col with opponent (or adjacent alignment).
        line_pen = 0.0
        if ny == oy:
            line_pen += 3.0
        if nx == ox:
            line_pen += 3.0
        if abs(nx - ox) + abs(ny - oy) == 1:
            line_pen += 1.5

        # Small preference to reduce distance to board center (avoids getting stuck near edges)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_score = -0.12 * md(nx, ny, cx, cy)

        score = res_score + opp_score + center_score - line_pen

        # Deterministic tie-break: prefer moves with smaller (dx,dy) lexicographic order to reduce jitter
        if score > best_score or (score == best_score and best is not None and (dx, dy) < (best[0], best[1])):
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]