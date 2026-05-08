def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles if len(p) >= 2)
    if (sx, sy) in set((p[0], p[1]) for p in resources if len(p) >= 2):
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst
    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obst:
            continue
        d1 = dist(sx, sy, rx, ry)
        d2 = dist(ox, oy, rx, ry)
        lead = d2 - d1  # positive if we are closer
        key = (-lead, d1, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        tx, ty = (w // 2, h // 2)
    else:
        tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    # prefer direct move; then closer-to-target among valid 1-step moves
    for ddx, ddy in [(dx, dy)] + [m for m in moves if m != (dx, dy)]:
        nx, ny = sx + ddx, sy + ddy
        if valid(nx, ny):
            d = dist(nx, ny, tx, ty)
            candidates.append((d, -abs(ddx), -abs(ddy), ddx, ddy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][3]), int(candidates[0][4])]