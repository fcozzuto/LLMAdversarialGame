def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        cx, cy = w // 2, h // 2
        best_key = None
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dC = man(nx, ny, cx, cy)
            dO = man(nx, ny, ox, oy)
            key = (dC, -dO, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    best_overall = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        best_res = None
        for rx, ry in resources:
            dS = man(nx, ny, rx, ry)
            dO = man(nx, ny, rx, ry)
            gap = dO - dS  # higher means we're closer than opponent
            t = (gap, -dS, -dO, rx, ry)
            if best_res is None or t > best_res:
                best_res = t
        # prefer stronger gap; then smaller self distance via -dS in best_res; tie-break by move order
        key = (best_res[0], best_res[1], -best_res[2], dx, dy)
        if best_overall is None or key > best_overall:
            best_overall = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]