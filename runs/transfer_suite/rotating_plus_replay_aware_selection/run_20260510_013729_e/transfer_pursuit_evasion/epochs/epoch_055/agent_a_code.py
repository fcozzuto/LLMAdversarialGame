def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    if not (0 <= sx < w and 0 <= sy < h):
        sx, sy = 0, 0

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cost(nx, ny):
        if (nx, ny) in obs:
            return 10**9
        dx = abs(nx - ox)
        dy = abs(ny - oy)
        cheb = dx if dx > dy else dy
        man = dx + dy
        adj_block = 0
        for tx, ty in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (nx + tx, ny + ty) in obs:
                adj_block += 1
        diag_bonus = 1.0 if dx > 0 and dy > 0 else 0.0
        # prioritize cutting distance (chebyshev), then diagonal alignment, then avoid clutter near obstacles
        return cheb * 1.0 + man * 0.08 - diag_bonus * 0.25 + adj_block * 0.35

    best = (0, 0)
    best_c = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            c = cost(nx, ny)
            if c < best_c or (c == best_c and (dx, dy) == (0, 0)):
                best_c = c
                best = (dx, dy)
    return [int(best[0]), int(best[1])]