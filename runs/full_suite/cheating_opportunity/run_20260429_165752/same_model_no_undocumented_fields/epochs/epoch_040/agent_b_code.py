def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        # Deterministic drift to center-ish
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, tx, ty)
            key = (d, dx == 0 and dy == 0)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    best_move = None
    best_key = None
    # Choose target that we can reach earlier than opponent; tie-break by my distance then target position
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_best = None
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Higher (od-md) is better; smaller md is better; lexicographic target for determinism
            key = (-(od - md), md, rx, ry)
            if my_best is None or key < my_best[0]:
                my_best = (key, (rx, ry), md, od)
        # Prefer moves that maximize advantage; also break ties by prefer staying mobile towards closer resource
        key2 = (my_best[0][0], my_best[0][1], my_best[0][2], my_best[0][3], abs(dx), abs(dy))
        if best_key is None or key2 < best_key:
            best_key = key2
            best_move = [dx, dy]

    return best_move