def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_score = -10**18
    best_move = [0, 0]

    if res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            md = min(abs(nx - rx) + abs(ny - ry) for (rx, ry) in res)
            oppd = abs(nx - ox) + abs(ny - oy)
            score = -md * 10 - max(0, 4 - oppd) * 7 + (0 if (nx, ny) != (ox, oy) else -10)
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            oppd = abs(nx - ox) + abs(ny - oy)
            score = oppd * 2 - (0 if dx == 0 and dy == 0 else 0)
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move