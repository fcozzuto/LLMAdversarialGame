def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    # Race heuristic: prefer resources where we can beat opponent (more negative margin),
    # and then closer to us.
    best = None
    for x, y in resources:
        d1 = abs(x - sx) + abs(y - sy)
        d2 = abs(x - ox) + abs(y - oy)
        margin = d1 - d2
        key = (margin, d1, x, y)
        if best is None or key < best[0]:
            best = (key, (x, y))
    tx, ty = best[1]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        nd = abs(tx - nx) + abs(ty - ny)
        od = abs(tx - ox) + abs(ty - oy)
        # Prefer getting closer; slight preference to reduce (your distance - opponent distance).
        score = (nd - (od - abs(tx - sx) - abs(ty - sy)) // 1000, nd, nx, ny, dx, dy)
        if bestm is None or score < bestm[0]:
            bestm = (score, [dx, dy])

    if bestm is None:
        return [0, 0]
    return bestm[1]