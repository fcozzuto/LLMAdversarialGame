def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    unclaimed = observation.get("unclaimed_cells", []) or []
    opp_cells = set()
    for p in (observation.get("opponent_territory", []) or []):
        try:
            opp_cells.add((p[0], p[1]))
        except Exception:
            pass

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def d2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Pick a deterministic target from unclaimed; if none, aim near opponent.
    best_t = None
    if unclaimed:
        for x, y in unclaimed:
            if not inb(x, y):
                continue
            adj = 0
            for dx, dy in neigh8:
                if (x + dx, y + dy) in opp_cells:
                    adj = 1
                    break
            edge = 1 if x in (0, w - 1) or y in (0, h - 1) else 0
            val = d2(sx, sy, x, y) - 20 * adj - 5 * edge
            if best_t is None or val < best_t[0]:
                best_t = (val, x, y)
    if best_t is None:
        tx, ty = ox, oy
    else:
        tx, ty = best_t[1], best_t[2]

    unclaimed_set = set()
    for p in unclaimed:
        try:
            unclaimed_set.add((p[0], p[1]))
        except Exception:
            pass

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = -d2(nx, ny, tx, ty)
        if (nx, ny) in unclaimed_set:
            score += 30
        adj_opp = 0
        for ex, ey in neigh8:
            if (nx + ex, ny + ey) in opp_cells:
                adj_opp = 1
                break
        score += 6 * adj_opp
        if nx in (0, w - 1) or ny in (0, h - 1):
            score += 2
        score -= 0.05 * d2(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    dx, dy = best_move
    return [int(dx), int(dy)]