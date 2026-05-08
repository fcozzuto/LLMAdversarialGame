def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def add_cells(key, out):
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    out.add((x, y))

    un = set()
    oppT = set()
    add_cells("unclaimed_cells", un)
    add_cells("opponent_territory", oppT)

    res = set()
    if isinstance(observation.get("resources"), (list, tuple)):
        for p in observation.get("resources") or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    res.add((x, y))

    if (sx, sy) in obstacles:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18
    targets = list(un) if un else (list(res) if res else (list(oppT) if oppT else [(ox, oy)]))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        if un:
            d = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
        else:
            d = abs(nx - ox) + abs(ny - oy)

        score = -d
        if (nx, ny) in un:
            score += 2000
        if (nx, ny) in res:
            score += 400
        if (nx, ny) in oppT:
            score += 150
        if dx == 0 and dy == 0:
            score -= 5
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]