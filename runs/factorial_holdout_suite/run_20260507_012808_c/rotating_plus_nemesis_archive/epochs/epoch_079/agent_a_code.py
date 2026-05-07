def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    def md(a, b):
        return abs(a[0] - b[0]) if abs(a[0] - b[0]) > abs(a[1] - b[1]) else abs(a[1] - b[1])

    res_set = set(resources)
    if (sx, sy) in res_set:
        return [0, 0]

    # Deterministic ordering: prefer moves that get us on a resource; then closer to a resource where we outrun opponent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        # Evaluate by best resource we could target from this move.
        move_score = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_self = md((nx, ny), (rx, ry))
            d_opp = md((ox, oy), (rx, ry))
            # Big reward for immediate capture (chebyshev distance 0).
            score = 0
            if d_self == 0:
                score += 10**9
            # Prefer smaller distance; also prefer resources where we are currently closer than opponent.
            score += -1000 * d_self
            score += 200 * (d_opp - d_self)
            # Slight bias toward central area to reduce being corner-trapped by obstacles.
            score += -(abs((nx - (w - 1) / 2.0))) - (abs((ny - (h - 1) / 2.0)))
            if score > move_score:
                move_score = score
        # Tie-break deterministically: smaller dx, then smaller dy, then smaller Manhattan-ish from origin
        if move_score > best_score or (move_score == best_score and (dx, dy) < best_move):
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]