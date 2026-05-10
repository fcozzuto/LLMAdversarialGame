def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    ox, oy = observation.get("opponent_position", (x, y))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    candidates = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if inb(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def manh(a, b):
        ax, ay = a
        bx, by = b
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    def adj_counts(cx, cy):
        cu = 0
        co = 0
        cs = 0
        for ddx, ddy in dirs:
            if ddx == 0 and ddy == 0:
                continue
            nx, ny = cx + ddx, cy + ddy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            if (nx, ny) in unclaimed:
                cu += 1
            if (nx, ny) in oppT:
                co += 1
            if (nx, ny) in selfT:
                cs += 1
        return cu, co, cs

    best = None
    best_score = -10**9
    d0 = manh((x, y), (ox, oy))
    for dx, dy, nx, ny in candidates:
        score = 0
        if (nx, ny) in oppT:
            score += 18
        elif (nx, ny) in unclaimed:
            score += 12
        elif (nx, ny) in selfT:
            score += 4
        else:
            score += 1

        cu, co, cs = adj_counts(nx, ny)
        score += 2 * cu + 3 * co + 1 * cs

        d1 = manh((nx, ny), (ox, oy))
        score += (d1 - d0) * 0.25  # avoid drifting into opponent

        # If we're adjacent to opponent territory, prefer counterclaim moves.
        if co > 0:
            score += 3

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]