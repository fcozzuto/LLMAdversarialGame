def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def norm_cells(v):
        out = []
        if not v:
            return out
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.append((x, y))
        return out

    obstacles = set(norm_cells(observation.get("obstacles")))
    targets = norm_cells(observation.get("unclaimed_cells"))
    r = norm_cells(observation.get("resources"))
    if not targets and r:
        targets = r

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy))

    if not targets:
        return [0, 0]

    targets = sorted(set(targets))
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_score = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        dmin = 10**9
        for tx, ty in targets[:30]:
            d = man(nx, ny, tx, ty)
            if d < dmin:
                dmin = d
        dout = 10**9
        for tx, ty in [(ox, oy)]:
            dout = man(nx, ny, tx, ty)
        score = (-dmin) + 0.01 * dout
        key = (score, -dout, -dmin, dx, dy)
        if best is None or key > best_score:
            best_score = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]