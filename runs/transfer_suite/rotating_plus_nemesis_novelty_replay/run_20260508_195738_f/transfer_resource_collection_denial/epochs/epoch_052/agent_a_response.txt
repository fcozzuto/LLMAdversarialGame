def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = corners[(sx + sy * 3 + ox + oy * 5) % 4]
        best = (-10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            sc = (man(nx, ny, ox, oy) - man(nx, ny, tx, ty) * 0.25) - 0.01 * (nx + 2 * ny)
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    resources_sorted = sorted(resources, key=lambda r: (man(sx, sy, r[0], r[1]) + 2 * man(ox, oy, r[0], r[1]), r[0], r[1]))
    candidates = resources_sorted[:min(6, len(resources_sorted))]

    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # evaluate best target from this next position
        local_best = -10**18
        for tx, ty in candidates:
            self_d = man(nx, ny, tx, ty)
            opp_d = man(ox, oy, tx, ty)
            take = 10**6 if (nx, ny) == (tx, ty) else 0
            # Prefer being strictly earlier; penalize targets opponent is already closer to.
            race = (opp_d - self_d) * 50 - self_d
            block = 0
            if opp_d < self_d:
                block = -(self_d - opp_d) * 30
            local_best = max(local_best, take + race + block - 0.001 * (tx + 2 * ty))
        # Small preference to avoid staying if equal
        stay_pen = 2 if (dx == 0 and dy == 0) else 0
        sc = local_best - stay_pen - 0.001 * (nx + 3 * ny)
        if sc > best[0]:
            best = (sc, dx, dy)
    return [int(best[1]), int(best[2])]