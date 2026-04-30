def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def blocked(x, y):
        return x < 0 or y < 0 or x >= w or y >= h or (x, y) in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not blocked(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [tuple(r) for r in resources if tuple(r) not in obstacles]
    best_move = legal[0]
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        val = 0

        # avoid getting too close to opponent
        dO = md(nx, ny, ox, oy)
        if dO == 0:
            val -= 10000
        else:
            val -= 200 // dO

        # prefer immediate resource
        if (nx, ny) in obstacles:
            val -= 10000
        else:
            val += 1200 if (nx, ny) in res else 0

        # aim toward best resource by relative advantage
        if res:
            nearest_diff = None
            for rx, ry in res:
                dS = md(nx, ny, rx, ry)
                dP = md(ox, oy, rx, ry)
                diff = dP - dS  # positive means we are closer
                if nearest_diff is None or diff > nearest_diff:
                    nearest_diff = diff
            # convert advantage into score, plus slight preference for closeness
            val += (nearest_diff if nearest_diff is not None else 0) * 30
            # also nudge toward some resource generally
            d_any = min(md(nx, ny, rx, ry) for (rx, ry) in res)
            val += max(0, 24 - d_any)

        # slight penalty for near obstacles (local only)
        for ax, ay in obstacles:
            if abs(ax - nx) <= 1 and abs(ay - ny) <= 1 and (ax, ay) != (nx, ny):
                val -= 5

        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]