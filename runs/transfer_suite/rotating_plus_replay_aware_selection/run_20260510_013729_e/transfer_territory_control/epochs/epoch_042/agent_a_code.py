def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    xp, yp = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [0, 0]
    xo, yo = int(op[0]), int(op[1])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    myt = to_set("self_territory")
    opt = to_set("opponent_territory")

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    cand = []
    for dx, dy in moves:
        nx, ny = xp + dx, yp + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 40
        if (nx, ny) in myt:
            score += 10
        if (nx, ny) in opt:
            score -= 30
        score += - (abs(nx - xo) + abs(ny - yo)) * 0.5
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score += - (abs(nx - cx) + abs(ny - cy)) * 0.05
        cand.append((score, dx, dy))

    if not cand:
        return [0, 0]

    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(cand[0][1]), int(cand[0][2])]