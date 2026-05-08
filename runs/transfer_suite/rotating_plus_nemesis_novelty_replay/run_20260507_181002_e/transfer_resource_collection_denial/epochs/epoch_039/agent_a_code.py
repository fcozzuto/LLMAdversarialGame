def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not res:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = None
    for cell in res:
        sd = man((sx, sy), cell)
        od = man((ox, oy), cell)
        # Prefer resources we can reach strictly earlier; otherwise pick the one that reduces opponent advantage most.
        reach_margin = od - sd
        key = (reach_margin, -sd, - (cell[0] + cell[1]))
        if best_key is None or key > best_key:
            best_key = key
            best = cell

    tx, ty = best
    cx, cy = sx, sy

    def step_toward(cx, cy, tx, ty):
        dx = 0 if tx == cx else (1 if tx > cx else -1)
        dy = 0 if ty == cy else (1 if ty > cy else -1)
        return dx, dy

    cand = step_toward(cx, cy, tx, ty)
    x1, y1 = cx + cand[0], cy + cand[1]
    if 0 <= x1 < w and 0 <= y1 < h and (x1, y1) not in obs:
        return [cand[0], cand[1]]

    # If blocked, choose an alternative neighbor that keeps us closest and maintains advantage.
    best2 = (0, 0)
    bestk2 = None
    for dx, dy in dirs:
        nx, ny = cx + dx, cy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        sd = man((nx, ny), (tx, ty))
        od = man((ox, oy), (tx, ty))
        k = (od - sd, -sd, -(nx + ny))
        if bestk2 is None or k > bestk2:
            bestk2 = k
            best2 = (dx, dy)

    return [int(best2[0]), int(best2[1])]