def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_to_ours(x, y):
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            if (x + dx, y + dy) in selft:
                return True
        return False

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    frontier = []
    for cell in unclaimed:
        if adj_to_ours(cell[0], cell[1]):
            frontier.append(cell)
    for cell in opp:
        if adj_to_ours(cell[0], cell[1]):
            frontier.append(cell)

    def score_cell(x, y):
        d = abs(x - sx) + abs(y - sy)
        # prefer immediate flipping/expansion: opponent cells > unclaimed > far
        base = 0
        if (x, y) in opp:
            base += 500
        if (x, y) in unclaimed:
            base += 200
        # slight preference toward center to avoid corner stall
        center_pref = - (abs(x - cx) + abs(y - cy)) * 2
        return -base + d * 3 - center_pref

    targets = frontier if frontier else list(unclaimed) if unclaimed else list(opp)
    target = None
    if targets:
        best = 10**18
        for x, y in targets:
            if not inb(x, y) or (x, y) in obs:
                continue
            s = score_cell(x, y)
            if s < best:
                best = s
                target = (x, y)

    if target is None:
        return [0, 0]

    tx, ty = target
    best_move = (0, 0)
    best_val = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # discourage stepping into opponent when it doesn't reduce distance to target
        step_to = abs(nx - tx) + abs(ny - ty)
        opp_pen = -250 if (nx, ny) in opp else 0
        un_pen = -120 if (nx, ny) in unclaimed else 0
        val = step_to * 10 - opp_pen - un_pen
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]