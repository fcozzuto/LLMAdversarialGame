def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    targets = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                targets.append((x, y))

    if not targets:
        for p in observation.get("unclaimed_cells") or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if (x, y) not in obstacles:
                    targets.append((x, y))

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if targets:
        tx, ty = min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy) - 0.15 * (abs(t[0] - ox) + abs(t[1] - oy)))
    else:
        tx, ty = cx, cy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best = (10**9, None)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        val = abs(nx - tx) + abs(ny - ty)
        if val < best[0]:
            best = (val, [dx, dy])

    if best[1] is not None:
        return best[1]
    return [0, 0]