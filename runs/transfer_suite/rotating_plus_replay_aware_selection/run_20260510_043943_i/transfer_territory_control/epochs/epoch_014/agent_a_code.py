def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sx), int(sy)
    opp = observation.get("opponent_position", [None, None]) or [None, None]
    ox = int(opp[0]) if opp[0] is not None else -10**9
    oy = int(opp[1]) if opp[1] is not None else -10**9

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    targets = []
    for key in ("unclaimed_cells", "resources"):
        for c in (observation.get(key, []) or []):
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                targets.append((int(c[0]), int(c[1])))
        if targets:
            break

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    if targets:
        tx, ty = targets[0]
        best_t = (sx - tx) ** 2 + (sy - ty) ** 2
        for (x, y) in targets[1:]:
            d = (sx - x) ** 2 + (sy - y) ** 2
            if d < best_t or (d == best_t and (x, y) < (tx, ty)):
                tx, ty, best_t = x, y, d
    else:
        tx, ty = ox, oy

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_t = (nx - tx) ** 2 + (ny - ty) ** 2
        d_o = (nx - ox) ** 2 + (ny - oy) ** 2
        v = -d_t + 0.05 * d_o
        if (best is None) or (v > best_val) or (v == best_val and (dx, dy) < best):
            best, best_val = (dx, dy), v

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return [int(best[0]), int(best[1])]