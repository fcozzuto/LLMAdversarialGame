def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    if (sx, sy) in obs:
        return [0, 0]
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs
    if not res:
        # drift toward opponent's side to potentially contest center resources
        tx = (w - 1 + sx) // 2
        ty = (h - 1 + sy) // 2
        best = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -abs(nx - tx) - abs(ny - ty) - 0.1 * (abs(nx - ox) + abs(ny - oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    res_set = set(res)
    if (sx, sy) in res_set:
        return [0, 0]

    def md(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    # choose a deterministic "primary" target: closest by Manhattan; ties by x then y
    res_sorted = sorted(res, key=lambda r: (md((sx, sy), r), r[0], r[1]))
    target = res_sorted[0]
    # also consider best "alternate" to avoid dead-ends
    alt = res_sorted[1] if len(res_sorted) > 1 else target

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # attractive: progress toward target, with a small fallback toward alternate
        d1 = md((nx, ny), target)
        d2 = md((nx, ny), alt)
        attractive = -d1 - 0.15 * d2
        # avoid tight spots: prefer moves that keep mobility
        neigh_free = 0
        for ddx, ddy in dirs:
            tx2, ty2 = nx + ddx, ny + ddy
            if legal(tx2, ty2):
                neigh_free += 1
        # cautious: slightly avoid moving closer to opponent unless we are on top of target
        cautious = 0.06 * (md((nx, ny), (ox, oy)) - md((sx, sy), (ox, oy)))
        # reward stepping onto a resource
        pickup = 1.7 if (nx, ny) in res_set else 0.0
        # discourage staying if it doesn't help
        stay_pen = 0.25 if (dx == 0 and dy == 0) else 0.0
        val = attractive + 0.22 * neigh_free + cautious + pickup - stay_pen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]