def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    resset = {(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2}
    obst = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    if (sx, sy) in resset:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    mypos = (sx, sy)
    opppos = (ox, oy)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obst:
            continue
        mydmin = 10**9
        delta_best = -10**9
        for r in resset:
            myd = md((nx, ny), r)
            od = md(opppos, r)
            if myd < mydmin:
                mydmin = myd
            delta = od - myd
            # Prefer picking up immediately, otherwise win-the-race against denier.
            if myd == 0:
                delta_best = 10**6
            else:
                if delta > delta_best:
                    delta_best = delta
        # If no resources, run to maximize distance from opponent.
        if not resset:
            obj = md((nx, ny), opppos)
        else:
            obj = delta_best - 0.02 * mydmin
        key = (obj, -nx, -ny, dx, dy)
        if best is None or key > best[0]:
            best = (key, (dx, dy))

    return [best[1][0], best[1][1]] if best else [0, 0]