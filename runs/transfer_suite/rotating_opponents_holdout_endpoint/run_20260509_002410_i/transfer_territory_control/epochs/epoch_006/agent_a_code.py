def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = p
            obstacles.add((x, y))
        except Exception:
            pass

    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])

    moves = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    best = None
    best_val = -10**18

    targets = unclaimed if unclaimed else (list(opp_t) if opp_t else [(ox, oy)])
    if not targets:
        targets = [(ox, oy)]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        md = abs(nx - sx) + abs(ny - sy)

        # pick nearest target to influence
        t = min(targets, key=lambda p: abs(nx - p[0]) + abs(ny - p[1]))
        dist_to_t = abs(nx - t[0]) + abs(ny - t[1])

        # heuristic: expand unclaimed, avoid opponent territory less, prefer our territory a bit
        val = -dist_to_t
        if (nx, ny) in unclaimed:
            val += 100000
        if (nx, ny) in opp_t:
            val -= 20000
        if (nx, ny) in self_t:
            val += 2000

        # slight tie-breaker toward moving closer to opponent when no targets
        if not unclaimed and opp_t:
            val += -2 * (abs(nx - ox) + abs(ny - oy))

        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        # fallback: try any in-bounds move even if blocked
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]