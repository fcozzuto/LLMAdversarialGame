def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(op[0]), int(op[1])

    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if p and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    cells = []
    for p in unclaimed:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                cells.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    tx, ty = None, None
    if cells:
        best = None
        bestd = 10**9
        for x, y in cells:
            d = man(sx, sy, x, y)
            if d < bestd or (d == bestd and (x, y) < best):
                bestd = d
                best = (x, y)
        tx, ty = best
    else:
        best = None
        bestd = -1
        for x in range(w):
            for y in range(h):
                if (x, y) in obstacles:
                    continue
                d = man(x, y, ox, oy)
                if d > bestd or (d == bestd and (x, y) < (best if best else (w, h))):
                    bestd = d
                    best = (x, y)
        tx, ty = best

    best_move = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = man(nx, ny, tx, ty)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]