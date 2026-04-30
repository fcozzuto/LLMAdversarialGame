def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def dist_cheb(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    if not resources:
        # head toward center deterministically
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx - sx, cy - sy
        dx = 0 if tx == 0 else (1 if tx > 0 else -1)
        dy = 0 if ty == 0 else (1 if ty > 0 else -1)
        return [dx, dy]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def min_dist(pos):
        best = None
        for r in resources:
            d = dist_cheb(pos, r)
            if best is None or d < best:
                best = d
                if best == 0:
                    return 0
        return best if best is not None else 10**9

    def candidate_score(nsx, nsy):
        if (nsx, nsy) in obstacles:
            return -10**12
        myd = min_dist((nsx, nsy))
        opd = min_dist((ox, oy))
        adv = opd - myd  # maximize advantage
        on_res = 1 if (nsx, nsy) in res_set else 0
        # small tie-break to move toward opponent-side resources
        corner_bias = (nsx + nsy) * 0.001
        return (adv * 100.0) + (on_res * 10000.0) - myd * 2.0 + corner_bias

    best_move = (0, 0)
    best_val = None
    # deterministic tie-break order by deltas list
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        val = candidate_score(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]