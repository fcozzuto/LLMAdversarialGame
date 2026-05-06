def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    rset = set(tuple(p) for p in resources)

    if not resources:
        tx = (w - 1) // 4 if ox > (w - 1) // 2 else (3 * (w - 1)) // 4
        ty = (h - 1) // 4 if oy > (h - 1) // 2 else (3 * (h - 1)) // 4
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, tx, ty)
            key = (-d, dx, dy)
            if best is None or key < best:
                best = key
        return [best[1], best[2]]

    # Evaluate each move by proximity to resources, with slight pressure to stay away from opponent.
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in rset:
            val = 1e9
        else:
            mind = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < mind:
                    mind = d
                    if mind == 0:
                        break
            val = 1000.0 / (mind + 1)  # closer is better
        # Pressure term: slightly prefer moves that increase distance from opponent.
        oppd = cheb(nx, ny, ox, oy)
        val += 0.06 * oppd
        # Small deterministic tie-breaker favoring upper-left-ish movement.
        key = (-val, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
    return [best_key[1], best_key[2]]