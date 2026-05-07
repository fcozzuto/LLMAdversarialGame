def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def blocked(x, y):
        return (x, y) in obs or not (0 <= x < w and 0 <= y < h)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    res_set = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if isinstance(rx, int) and isinstance(ry, int):
                res_set.add((rx, ry))

    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        # Immediate grab preference
        if (nx, ny) in res_set:
            return [dx, dy]

        # Choose a resource where we have the best distance advantage
        val = -10**12
        for rx, ry in res_set:
            if blocked(rx, ry):
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we reach first (or sooner)
            # Encourage approaching close resources even if not strictly leading
            v = 1000 * adv - 5 * ds
            if v > val:
                val = v

        # Deterministic tiebreaker: prefer moves that reduce our distance to the best resource we can aim at
        if val > best_val:
            best_val = val
            best = (dx, dy)
        elif val == best_val:
            if (abs(dx) + abs(dy), dx, dy) < (abs(best[0]) + abs(best[1]), best[0], best[1]):
                best = (dx, dy)

    return [int(best[0]), int(best[1])]