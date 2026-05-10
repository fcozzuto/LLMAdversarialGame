def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = r[0], r[1]
            if (x, y) not in obstacles and 0 <= x < w and 0 <= y < h:
                targets.append((x, y))
    if not targets:
        return [0, 0]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_dist(px, py):
        bd = None
        for tx, ty in targets:
            d = abs(px - tx) + abs(py - ty)
            if bd is None or d < bd:
                bd = d
        return bd if bd is not None else 10**9

    sd0 = best_dist(sx, sy)
    od0 = best_dist(ox, oy)

    best = None
    for dx, dy in dirs:
        nsx, nsy = sx + dx, sy + dy
        if not ok(nsx, nsy):
            continue
        nds = best_dist(nsx, nsy)
        ndo = best_dist(ox, oy)
        move_val = (nds, -(ndo - nds), dx, dy)
        if best is None or move_val < best[0]:
            best = (move_val, [dx, dy])

    return best[1] if best is not None else [0, 0]