def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {tuple(p) for p in obstacles}

    cand = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    if resources:
        best_move = [0, 0]
        bestv = -10**18
        # Deterministic: tie-break by lexicographic (dx,dy) via iteration order and >=
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            # Choose the resource that best supports this move (arrive early vs deny)
            move_best = -10**18
            for rx, ry in resources:
                ds = d2(nx, ny, rx, ry)
                do = d2(ox, oy, rx, ry)
                # Lower self distance and higher opponent distance is good
                v = -ds + 0.8 * do
                if v > move_best:
                    move_best = v
            if move_best > bestv:
                bestv = move_best
                best_move = [dx, dy]
        return best_move

    # No visible resources: drift to a safer corner (farther from opponent)
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: d2(c[0], c[1], ox, oy))
    best_move = [0, 0]
    bestv = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        v = -d2(nx, ny, tx, ty) - 0.5 * d2(nx, ny, ox, oy)
        if v > bestv:
            bestv = v
            best_move = [dx, dy]
    return best_move