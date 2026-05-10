def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or (W - 1, H - 1)
    ox, oy = int(op[0]), int(op[1])
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in blocked

    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []

    candidates = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                candidates.append((x, y))
    if not candidates:
        for p in unclaimed:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inside(x, y):
                    candidates.append((x, y))

    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
    if not candidates:
        candidates = [(int(round(cx)), int(round(cy))), (W - 1, H - 1), (0, 0), (W // 2, 0), (0, H // 2)]

    best = None
    best_s = None
    for x, y in candidates:
        ds = abs(x - sx) + abs(y - sy)
        do = abs(x - ox) + abs(y - oy)
        center_bias = abs(x - cx) + abs(y - cy)
        s = ds - 0.55 * do + 0.08 * center_bias
        if best_s is None or s < best_s or (s == best_s and (y, x) < (best[1], best[0])):
            best_s = s
            best = (x, y)
    tx, ty = best

    moves = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    bestm = None
    bestd = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = abs(tx - nx) + abs(ty - ny)
        if bestd is None or d < bestd or (d == bestd and (dx, dy) < bestm):
            bestd = d
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]