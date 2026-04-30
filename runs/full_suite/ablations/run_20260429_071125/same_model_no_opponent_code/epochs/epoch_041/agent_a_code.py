def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d_op = abs(nx - ox) + abs(ny - oy)
                cand = (-d_op, dx, dy)
                if best is None or cand < best:
                    best = cand
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    tx, ty = min(resources, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d_t = abs(nx - tx) + abs(ny - ty)
            d_op = abs(nx - ox) + abs(ny - oy)
            cand = (d_t, -d_op, dx, dy)
            if best is None or cand < best:
                best = cand

    if best is None:
        return [0, 0]
    return [best[2], best[3]]