def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dxdy = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_score = -10**18

    for dx, dy in dxdy:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        if (nx, ny) in oppT:
            val = 1000
        elif (nx, ny) in unclaimed:
            val = 200
        elif (nx, ny) in selfT:
            val = 20
        else:
            val = 60  # rare: should be unclaimed/territory but handle generically

        # Encourage approaching target: nearest unclaimed/opp territory
        # (use simple local heuristic for speed/determinism)
        d_center = abs(nx - cx) + abs(ny - cy)
        approach = -0.6 * d_center

        # If we can immediately contact opponent territory nearby, prioritize
        adj_opp = 0
        for adx, ady in dxdy:
            tx, ty = nx + adx, ny + ady
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in oppT:
                adj_opp += 1

        # Boundary pressure: move toward squares adjacent to opponent territory
        boundary = 40 * adj_opp

        score = val + approach + boundary

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best