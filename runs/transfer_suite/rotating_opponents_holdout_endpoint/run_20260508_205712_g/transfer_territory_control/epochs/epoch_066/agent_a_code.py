def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    self_x, self_y = int(sp[0]), int(sp[1])
    cx, cy = (w - 1) // 2, (h - 1) // 2

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2 and p[0] is not None and p[1] is not None:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]

    un = observation.get("unclaimed_cells") or []
    un_cells = []
    for p in un:
        if p and len(p) >= 2 and p[0] is not None and p[1] is not None:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                un_cells.append((x, y))
    if un_cells:
        best = None
        best_d = 10**18
        for x, y in un_cells:
            d = abs(x - cx) + abs(y - cy)
            if d < best_d or (d == best_d and (x, y) < best):
                best_d, best = d, (x, y)
        tx, ty = best
        dx, dy = 0, 0
        if tx > self_x: dx = 1
        elif tx < self_x: dx = -1
        if ty > self_y: dy = 1
        elif ty < self_y: dy = -1
        candidates = []
        for mx, my in moves:
            nx, ny = self_x + mx, self_y + my
            if valid(nx, ny):
                dd = abs(nx - tx) + abs(ny - ty)
                candidates.append((dd, mx, my))
        if candidates:
            candidates.sort()
            return [candidates[0][1], candidates[0][2]]

    best = None
    best_d = 10**18
    for mx, my in moves:
        nx, ny = self_x + mx, self_y + my
        if not valid(nx, ny):
            continue
        d = abs(nx - cx) + abs(ny - cy)
        if d < best_d or (d == best_d and (nx, ny) < best):
            best_d, best = d, (nx, ny)
    if best is None:
        return [0, 0]
    return [best[0] - self_x, best[1] - self_y]