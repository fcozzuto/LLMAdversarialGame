def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obst_pen(x, y):
        if (x, y) in occ:
            return 10**9
        pen = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            if (x+dx, y+dy) in occ:
                pen += 30
        for dx, dy in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            if (x+dx, y+dy) in occ:
                pen += 12
        return pen

    if not resources:
        return [0, 0]

    best = None
    best_sc = -10**18
    for rx, ry in resources:
        if (rx, ry) in occ:
            continue
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        sc = (do - ds) * 20 - ds - obst_pen(rx, ry) // 10
        # If we tie, prefer earlier along same side of opponent (stable deterministic)
        if sc > best_sc or (sc == best_sc and (rx, ry) < best):
            best_sc = sc
            best = (rx, ry)

    tx, ty = best
    best_move = (0, 0)
    best_val = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = dist(nx, ny, tx, ty) * 3 + obst_pen(nx, ny)
        # keep pressure toward target; mildly avoid giving opponent closer access by symmetry
        val += (dist(ox, oy, tx, ty) - dist(ox, oy, nx, ny)) * 0.01
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]