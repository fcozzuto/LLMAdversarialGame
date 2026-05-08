def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_mv = (0, 0)
    best_sc = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        sc = 0
        if (nx, ny) in selfT:
            sc += 1
        elif (nx, ny) in unclaimed:
            sc += 4
        elif (nx, ny) in oppT:
            sc += 8  # flipping on entry
        else:
            sc += 2

        d_opp = man(nx, ny, ox, oy)
        if d_opp <= 1:
            sc -= 5
        elif d_opp <= 2:
            sc -= 2

        d_center = abs(nx - cx) + abs(ny - cy)
        sc += 2.0 * (w + h - d_center)

        if (nx, ny) not in selfT:
            sc += 1
        if (nx, ny) in oppT and d_opp <= 2:
            sc += 1  # allow opportunistic flips near their frontier

        if sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]