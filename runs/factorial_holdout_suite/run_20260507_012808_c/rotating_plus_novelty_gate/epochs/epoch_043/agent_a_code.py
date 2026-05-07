def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = 0 if sx < 0 else (w - 1 if sx >= w else int(sx))
    sy = 0 if sy < 0 else (h - 1 if sy >= h else int(sy))
    ox = 0 if ox < 0 else (w - 1 if ox >= w else int(ox))
    oy = 0 if oy < 0 else (h - 1 if oy >= h else int(oy))

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources") or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w - 1 - sx, h - 1 - sy
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # prefer targets we can reach earlier; if close, prefer higher chance by lead margin
            lead = opd - myd
            # mild tie-break to reduce dithering: prefer nearer to us after accounting for lead
            key = (-(lead * 4) + myd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    # choose deterministic move among 9 options, avoiding obstacles and reducing distance
    options = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                options.append((dx, dy))
    if not options:
        return [0, 0]

    current_d = cheb(sx, sy, tx, ty)
    best = None
    best_key = None
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        nd = cheb(nx, ny, tx, ty)
        # discourage moving away; slight preference for progressing in x then y for determinism
        away_pen = (nd - current_d)
        # also avoid stepping adjacent to obstacles too often (simple local proxy)
        adj_obs = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                ax, ay = nx + ex, ny + ey
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                    adj_obs += 1
        key = (away_pen, nd, adj_obs, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]