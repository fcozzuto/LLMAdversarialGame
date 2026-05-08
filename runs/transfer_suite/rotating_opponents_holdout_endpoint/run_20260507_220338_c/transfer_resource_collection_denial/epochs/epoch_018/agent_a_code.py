def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (0, 1), (1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    best_move = (0, 0)
    best_val = -10**30

    # Evaluate only a few closest resources for speed and stability.
    res_info = []
    for rx, ry in resources:
        sd0 = md(sx, sy, rx, ry)
        res_info.append((sd0, rx, ry))
    res_info.sort(key=lambda t: t[0])
    top = res_info[:6]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        # Base positional pressure vs opponent.
        for _, rx, ry in top:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            if nx == rx and ny == ry:
                val += 10**9
            else:
                # Prefer resources where we are closer than opponent.
                closer = od - sd
                val += closer * 180 - sd * 6
                # Slightly reward reducing opponent's advantage.
                if od < sd:
                    val -= (sd - od) * 25

        # If we can't hit a top resource, still drift toward the nearest.
        if val == 0:
            if top:
                val = -top[0][0]

        # Deterministic tie-break: prefer smaller |dx|+|dy|, then lexicographic.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            def tiekey(m):
                mx, my = m
                return (abs(mx) + abs(my), mx, my)
            if tiekey((dx, dy)) < tiekey(best_move):
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]