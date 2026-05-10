def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best = None
    bestv = -10**18

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            v = d  # maximize separation
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best if best is not None else [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        mind = 10**9
        for rx, ry in resources:
            dist = abs(nx - rx) + abs(ny - ry)
            if dist < mind:
                mind = dist
        dpo = abs(nx - ox) + abs(ny - oy)
        v = -mind * 10 + dpo  # prioritize reaching resources, then avoid opponent
        if v > bestv:
            bestv, best = v, [dx, dy]

    return best if best is not None else [0, 0]