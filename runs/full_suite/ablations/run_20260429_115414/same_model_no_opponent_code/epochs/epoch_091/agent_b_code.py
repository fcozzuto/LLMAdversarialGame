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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_t = None
        best_v = -10**18
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources that we reach sooner than opponent; also break ties by closeness.
            v = (od - sd) * 1000 - sd
            if v > best_v:
                best_v = v
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_mval = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        # Secondary: if equal, prefer moves that increase opponent distance from target.
        od = cheb(ox, oy, tx, ty)
        v = d_to_target * 1000 - (od - cheb(ox, oy, tx, ty))  # keep deterministic, effectively just d
        if v < best_mval:
            best_mval = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]