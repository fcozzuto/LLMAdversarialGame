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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def nearest_dist(x, y):
        if not resources:
            return 10**9
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_opp = nearest_dist(ox, oy)
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        d_our = nearest_dist(nx, ny)
        # Prefer moves that put us closer to resources than the opponent, and keep opponent farther.
        d_opp = cur_opp  # opponent position unchanged this turn; still use as a consistent baseline
        score = (d_opp - d_our) * 10

        # Nudge toward central area and away from walls if equally ranked
        center_bias = -(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        score += int(center_bias * 2)

        # Small obstacle-avoidance: penalize standing next to obstacles
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    adj_pen += 1
        score -= adj_pen

        if score > best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]