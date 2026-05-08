def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    op = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = map(int, op)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = (0, 0)
    best_sc = -10**9
    # Prefer a direction that advances toward center and can claim/flip while keeping distance from the opponent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        sc = 0
        if (nx, ny) in unclaimed:
            sc += 7
        if (nx, ny) in oppT:
            sc += 9
        if (nx, ny) in selfT:
            sc += 3

        # Center pressure
        sc += int(3 * (-(man(nx, ny, cx, cy) - man(sx, sy, cx, cy))))

        # Avoid being counterclaimed: keep/extend distance from opponent
        d0 = man(sx, sy, ox, oy)
        d1 = man(nx, ny, ox, oy)
        if d1 > d0:
            sc += 4
        else:
            sc -= 2

        # Mild obstacle-adjacent preference to reduce getting stuck
        adj_free = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if inside(ax, ay):
                adj_free += 1
        sc += adj_free * 0.2

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
        elif sc == best_sc:
            # Deterministic tie-break: prefer staying still, then lexicographically.
            if (dx, dy) == (0, 0) and best != (0, 0):
                best = (dx, dy)
            elif (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]