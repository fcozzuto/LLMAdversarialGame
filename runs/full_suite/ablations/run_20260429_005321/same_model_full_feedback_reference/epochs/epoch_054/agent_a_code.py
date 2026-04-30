def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def eval_move(nx, ny):
        if resources:
            best = -10**18
            for rx, ry in resources:
                my = d2(nx, ny, rx, ry)
                opp = d2(ox, oy, rx, ry)
                # Prefer resources where we are closer than opponent; avoid giving them easy captures.
                v = (opp - my) - my * 0.02
                # If we can step onto the resource, prioritize strongly.
                if nx == rx and ny == ry:
                    v += 10**6
                # Slightly prefer fewer total steps to the best overall resource.
                best = v if v > best else best
            return best
        cx, cy = (w - 1) // 2, (h - 1) // 2
        return -d2(nx, ny, cx, cy)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = eval_move(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]