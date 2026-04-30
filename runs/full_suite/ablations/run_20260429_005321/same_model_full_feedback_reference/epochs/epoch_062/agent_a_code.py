def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_val = 10**18

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            # Prefer resources we can reach quickly, especially those opponent is far from.
            v_best = 10**18
            for rx, ry in resources:
                our = d2(nx, ny, rx, ry)
                opp = d2(ox, oy, rx, ry)
                val = our - 0.55 * opp
                if val < v_best:
                    v_best = val
            # Slight preference to keep distance when values tie.
            v = v_best + 0.03 * d2(nx, ny, ox, oy)
            if v < best_val:
                best_val = v
                best_move = (dx, dy)
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            v = d2(nx, ny, cx, cy) - 0.12 * d2(nx, ny, ox, oy)
            if v < best_val:
                best_val = v
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]