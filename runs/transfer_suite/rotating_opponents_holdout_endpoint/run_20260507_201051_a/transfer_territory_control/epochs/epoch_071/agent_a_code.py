def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for c in unclaimed:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if inside(x, y) and (x, y) not in obs:
                targets.append((x, y))

    if not targets:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = None, None
        bestd = None
        for x, y in targets:
            d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
            if bestd is None or d < bestd:
                bestd = d
                tx, ty = x, y

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        d1 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        d2 = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty) if tx is not None else 0
        score = d2 * 2 - d1  # go toward target; prefer being farther from opponent
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]