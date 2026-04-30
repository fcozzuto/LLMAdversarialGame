def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        d_me = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        key = (d_me, -d_opp, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    if best_r is not None:
        tx, ty = best_r
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            cand.append((cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy), dx, dy))
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            cand.append((cheb(nx, ny, tx, ty), dx, dy))

    if not cand:
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                return [int(dx), int(dy)]
        return [0, 0]

    best = sorted(cand)[0]
    if best_r is not None:
        return [int(best[2]), int(best[3])]
    return [int(best[1]), int(best[2])]