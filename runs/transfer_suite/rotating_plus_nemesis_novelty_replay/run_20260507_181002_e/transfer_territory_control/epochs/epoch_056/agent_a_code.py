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
    if not unclaimed:
        unclaimed = toset(observation.get("resources"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    if not unclaimed:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_val = -10**18
    for tx, ty in unclaimed:
        if (tx, ty) in obstacles:
            continue
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        if ds == 0 and (tx, ty) not in selfT:
            continue
        adj = 0
        for dx, dy in neigh8:
            if (tx + dx, ty + dy) in selfT:
                adj += 1
        center = - (abs(tx - cx) + abs(ty - cy))
        # Prefer: reachable soon, advantage over opponent, and near our current territory.
        val = (-ds) + (do * 0.9) + (adj * 2.5) + (center * 0.2)
        if (tx, ty) in oppT:
            val += 1.5  # allow flipping closer in if encountered by sweeping
        if val > best_val or (val == best_val and (tx, ty) < best):
            best_val = val
            best = (tx, ty)

    tx, ty = best
    curd = md(sx, sy, tx, ty)
    best_step = (0, 0)
    best_sd = curd
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd = md(nx, ny, tx, ty)
        do = md(ox, oy, tx, ty)
        # Tie-break: step that improves our immediate claim pressure.
        cand = sd - do * 0.0001 - ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 1e-6
        best_cand = best_sd - do * 0.0001 - ((sx - cx) * (sx - cx) + (sy - cy) * (sy - cy)) * 1e-6
        if cand < best_cand or (sd < best_sd and (dx, dy) < best_step):
            best_sd = sd
            best_step = (dx, dy)
        elif sd == best_sd and (dx, dy) < best_step:
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]