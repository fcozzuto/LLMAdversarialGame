def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    oppT = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    un = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selfT = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    oppPos = observation.get("opponent_position", None)
    cx, cy = (w // 2, h // 2)

    if (observation.get("opponent_territory_count", 0) or 0) > 0:
        mx = my = 0
        cnt = 0
        for x, y in oppT:
            mx += x
            my += y
            cnt += 1
        ox, oy = (mx // max(1, cnt), my // max(1, cnt))
    elif oppPos:
        ox, oy = oppPos[0], oppPos[1]
    else:
        ox, oy = (w - 1 - sx, h - 1 - sy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = -10**9

    # Encourage advancing toward center while converting opponent/claiming unclaimed, but avoid obstacles.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        v = 0
        if (nx, ny) in oppT:
            v += 8  # strong: flip opponent territory on entry
        if (nx, ny) in un:
            v += 5  # claim unclaimed
        if (nx, ny) in selfT:
            v += 1  # maintain momentum within control
        # Prefer approaching center, but not letting opponent center dominate; mix in distance tradeoff.
        dc = abs(nx - cx) + abs(ny - cy)
        do = abs(nx - ox) + abs(ny - oy)
        v += (-0.7 * dc) + (0.15 * do)
        # Slightly prefer moves that stay on/near our boundary: adjacent to unclaimed or opponent territory.
        adj = 0
        for ddx, ddy in moves:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and ((ax, ay) in un or (ax, ay) in oppT):
                adj += 1
        v += 0.2 * adj

        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1]) if best else False):
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]