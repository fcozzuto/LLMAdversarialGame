def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    unclaimed = observation.get("unclaimed_cells") or []
    uset = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}

    obstacles = observation.get("obstacles") or []
    oset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    opp_terr = observation.get("opponent_territory") or []
    opset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        d1 = x1 - x2
        if d1 < 0:
            d1 = -d1
        d2 = y1 - y2
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    targets = uset if uset else (opset if opset else {(ox, oy)})
    best_move = (0, 0)
    best_score = -10**18
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in oset:
            continue
        dist_t = 10**9
        for tx, ty in targets:
            d = man(nx, ny, tx, ty)
            if d < dist_t:
                dist_t = d
        dist_o = man(nx, ny, ox, oy)
        cell_bonus = 2000 if (nx, ny) in uset else 0
        terr_bonus = 500 if (nx, ny) in opset else 0
        score = cell_bonus + terr_bonus - 2 * dist_t + dist_o // 2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]