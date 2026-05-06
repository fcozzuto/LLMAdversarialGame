def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    self_pos = (sx, sy)
    opp_pos = (ox, oy)
    best = None

    for tx, ty in resources:
        sd = man(self_pos, (tx, ty))
        od = man(opp_pos, (tx, ty))
        closer = sd <= od  # try to win resource race
        win_gap = od - sd  # bigger is better
        # Prefer winning race; then minimize sd; within ties maximize win_gap; final tie by position
        key = (0 if closer else 1, sd, -win_gap, tx, ty)
        if best is None or key < best[0]:
            best = (key, (tx, ty))

    _, (tx, ty) = best

    # Choose move that best reduces distance to target, with deterministic tie-break that also pressures opponent.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nsd = man((nx, ny), (tx, ty))
        nod = man((nx, ny), (ox, oy))  # proxy pressure: move that also approaches opponent
        # Key: primary minimize nsd, then minimize opponent proximity metric (closer is better), then move order
        key = (nsd, nod, dx, dy)
        if best_mv is None or key < best_mv[0]:
            best_mv = (key, (dx, dy))

    if best_mv is None:
        return [0, 0]
    return [int(best_mv[1][0]), int(best_mv[1][1])]