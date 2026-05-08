def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if len(p) >= 2)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    if (sx, sy) in obs:
        return [0, 0]

    def dist(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    res = []
    for r in resources:
        if len(r) >= 2:
            rx, ry = r[0], r[1]
            if inb(rx, ry) and (rx, ry) not in obs:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    best_t = res[0]
    best_key = None
    for rx, ry in res:
        dself = dist(sx, sy, rx, ry)
        dopp = dist(ox, oy, rx, ry)
        key = (dopp - dself, -dself, -abs((rx - ox) + (ry - oy)))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dnew = dist(nx, ny, rx, ry)
        ndopp = dist(ox, oy, rx, ry)
        adv = ndopp - dnew
        # Prefer increasing advantage first, then reducing distance, then moving toward resource diagonal-ish.
        score = (adv, -dnew, -abs((rx - nx) - (ry - ny)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]