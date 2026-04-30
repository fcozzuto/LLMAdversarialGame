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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    cx, cy = (w - 1) // 2, (h - 1) // 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if resources:
            my_center = d2(nx, ny, cx, cy)
            score = -0.001 * my_center
            # Choose best resource to maximize distance advantage (opp closer -> bad)
            local_best = -10**18
            for rx, ry in resources:
                myd = d2(nx, ny, rx, ry)
                opd = d2(ox, oy, rx, ry)
                gap = opd - myd
                # If we can capture immediately, heavily reward
                if (nx, ny) == (rx, ry):
                    gap += 10**6
                # Slightly prefer reducing our distance even if opponent is also near
                local_best = gap if gap > local_best else local_best
            score += local_best
        else:
            # No resources known: maximize distance from opponent and drift to center
            score = d2(nx, ny, ox, oy) - 0.01 * d2(nx, ny, cx, cy)

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best