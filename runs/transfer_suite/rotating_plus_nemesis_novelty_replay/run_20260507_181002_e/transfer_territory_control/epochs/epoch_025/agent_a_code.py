def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y):
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    targets = toset(observation.get("unclaimed_cells"))
    if not targets:
        targets = toset(observation.get("resources"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if targets:
        best_t = None
        best_d = None
        for tx, ty in targets:
            d = abs(tx - sx) + abs(ty - sy)
            if best_d is None or d < best_d or (d == best_d and (tx, ty) < best_t):
                best_d = d
                best_t = (tx, ty)
        tx, ty = best_t
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dist = abs(tx - nx) + abs(ty - ny)
            score = dist * 100 + abs(nx - ox) + abs(ny - oy) * 0
            if best_score is None or score < best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # Fallback: deterministic move that stays in-bounds and avoids obstacles, tends toward center
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = abs(cx - nx) + abs(cy - ny)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]