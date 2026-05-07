def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = list(observation.get("resources", []) or [])

    dxs = (-1, 0, 1)
    legal = []
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))

    if not legal:
        return [0, 0]
    if (sx, sy) in obstacles:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    if (sx, sy) in res_set:
        return [0, 0]

    if not resources:
        # Drift toward opponent to contest while avoiding obstacles
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = (abs(nx - ox) + abs(ny - oy), abs(nx - sx) + abs(ny - sy), dx, dy)
            if best is None or v < best:
                best = v
        return [best[2], best[3]]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Prefer states that keep a lead in reaching the same best resource
        best_cell = None
        for rx, ry in resources:
            ds = manh(nx, ny, rx, ry)
            do = manh(ox, oy, rx, ry)
            # maximize lead (opponent distance - self distance); then minimize self distance
            cand = (- (do - ds), ds, rx, ry)
            if best_cell is None or cand < best_cell:
                best_cell = cand
        # best_cell: (-lead, ds, rx, ry) -> primary minimize (-lead) means maximize lead
        cand2 = (best_cell[0], best_cell[1], dx, dy)
        if best is None or cand2 < best:
            best = cand2

    return [best[2], best[3]]