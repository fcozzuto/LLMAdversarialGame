def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    if not unclaimed:
        targets = list(oppT)[:]
        if not targets:
            return [0, 0]
    else:
        targets = list(unclaimed)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_score = -10**18
    for tx, ty in targets:
        if (tx, ty) in obstacles:
            continue
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        center = abs(tx - cx) + abs(ty - cy)
        edge = (tx == 0 or tx == w - 1 or ty == 0 or ty == h - 1)
        score = (do - ds) * 4.0 + (-0.25 * ds) + (-0.05 * center) + (0.2 if edge else 0.0)
        if (tx, ty) in selfT:
            score -= 1000.0
        if (tx, ty) in oppT:
            score += 1.5
        if score > best_score:
            best_score = score
            best = (tx, ty)

    tx, ty = best if best is not None else (sx, sy)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_md = 10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = md(nx, ny, tx, ty)
        if d < best_md:
            best_md = d
            best_move = (dx, dy)
        elif d == best_md:
            if (dx, dy) == (0, 0):
                best_move = best_move
    return [int(best_move[0]), int(best_move[1])]