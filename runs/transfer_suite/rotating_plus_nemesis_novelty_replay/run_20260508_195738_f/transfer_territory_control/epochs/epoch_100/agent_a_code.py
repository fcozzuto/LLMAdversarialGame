def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    px, py = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    myt = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opt = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    un = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_any(cset, x, y):
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            if (x + dx, y + dy) in cset:
                return True
        return False

    def manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        if (nx, ny) in un:
            score += 20.0
        if (nx, ny) in myt:
            score -= 1.0
        if adj_any(opt, nx, ny):
            score += 6.0
        if adj_any(myt, nx, ny):
            score += 2.0

        score -= 0.35 * manh(nx, ny, px, py)
        if un:
            dmin = 10**9
            for tx, ty in un:
                d = manh(nx, ny, tx, ty)
                if d < dmin:
                    dmin = d
            score -= 0.18 * dmin

        cand = (score, -manh(nx, ny, px, py), -dx, -dy, nx, ny)
        if best is None or cand > best:
            best = cand
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move