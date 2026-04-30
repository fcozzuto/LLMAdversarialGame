def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def score_for(nx, ny):
        if not res:
            # No visible resources: prefer moving away from opponent, avoid obstacles already filtered.
            dx = abs(nx - ox)
            dy = abs(ny - oy)
            return (dx if dx > dy else dy, -(abs(nx - ox) + abs(ny - oy)))
        # Prefer nearest resource; break ties by being farther from opponent.
        nxv = abs(nx - ox)
        nyv = abs(ny - oy)
        opp_cheb = nxv if nxv > nyv else nyv
        # Nearest resource distance (Manhattan), deterministic tie-breaking by opponent distance.
        best = None
        for rx, ry in res:
            d = abs(nx - rx) + abs(ny - ry)
            if best is None or d < best[0] or (d == best[0] and opp_cheb > best[1]):
                best = (d, opp_cheb)
        return (best[0], best[1])

    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        key = score_for(nx, ny)
        # Minimize resource distance, maximize opponent distance (via second component)
        if best_key is None or key[0] < best_key[0] or (key[0] == best_key[0] and key[1] > best_key[1]) or \
           (key[0] == best_key[0] and key[1] == best_key[1] and (dx, dy) < best_move):
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]