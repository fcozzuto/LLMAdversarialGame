def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (W - 1, H - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in blocked

    targets = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                targets.append((x, y))
    if not targets:
        for p in observation.get("unclaimed_cells") or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inside(x, y):
                    targets.append((x, y))
    if not targets:
        targets = [(W // 2, H // 2)]

    tx, ty = targets[0]
    bestd = None
    for x, y in targets:
        d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
        if bestd is None or d < bestd or (d == bestd and (x, y) < (tx, ty)):
            bestd, tx, ty = d, x, y

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    bestv = None
    bestm = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d1 = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        d2 = (ox - nx) * (ox - nx) + (oy - ny) * (ox - ny)
        v = (-d1) + 0.01 * d2
        if bestv is None or v > bestv or (v == bestv and (dx, dy) < bestm):
            bestv, bestm = v, (dx, dy)
    return [int(bestm[0]), int(bestm[1])]