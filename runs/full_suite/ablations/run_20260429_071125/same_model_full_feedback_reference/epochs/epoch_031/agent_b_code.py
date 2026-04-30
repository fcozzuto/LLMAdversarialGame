def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in moves:
            if ok(sx + dx, sy + dy):
                return [int(dx), int(dy)]
        return [0, 0]

    res = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 0
        if res:
            # pick closest resource by distance; prefer moving towards it
            md = None
            for rx, ry in res:
                d = (rx - nx) * (rx - nx) + (ry - ny) * (ry - ny)
                if md is None or d < md:
                    md = d
            score += -md
        else:
            # no known resources: move away from opponent
            score += ((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))
        # slight tie-breaker: keep away from opponent while resources exist
        score += 0.001 * (((sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)) - ((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)))
        if score > best_score:
            best_score = score
            best_move = [int(dx), int(dy)]

    return best_move