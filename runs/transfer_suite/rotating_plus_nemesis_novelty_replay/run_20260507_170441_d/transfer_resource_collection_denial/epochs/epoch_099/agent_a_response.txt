def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def opp_step_toward(tx, ty):
        best = None
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not ok(nx, ny):
                continue
            d = dist8(nx, ny, tx, ty)
            cand = (d, nx, ny)
            if best is None or cand < best:
                best = cand
        if best is None:
            return ox, oy
        return best[1], best[2]

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Choose best target resource for us, but evaluate assuming opponent also greedily moves toward it.
        local_best = -10**18
        for rx, ry in resources:
            my_now = dist8(nx, ny, rx, ry)
            ax, ay = opp_step_toward(rx, ry)
            opp_now = dist8(ax, ay, rx, ry)
            # Prefer being closer after both take a step; small bonus for directly reaching.
            val = (opp_now - my_now) * 100 - my_now
            if (nx, ny) == (rx, ry):
                val += 10000
            if (ox + 0, oy + 0) == (rx, ry):
                val -= 2000
            if val > local_best:
                local_best = val
        # Tie-break: prefer moves that reduce nearest resource distance for us.
        nearest = min(dist8(nx, ny, r[0], r[1]) for r in resources)
        val_total = local_best - nearest
        if val_total > best_val or (val_total == best_val and (dx, dy) < best_move):
            best_val = val_total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]