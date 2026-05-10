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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("pursuer" in opp_role and "evader" not in self_role)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def nearest_obst_dist(x, y):
        best = 9
        for (bx, by) in obstacles:
            d = cheb(x, y, bx, by)
            if d < best:
                best = d
                if best <= 0:
                    break
        return best

    best_move = [0, 0]
    best_val = -10**18 if is_pursuer else 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dist = cheb(nx, ny, ox, oy)

        # Predictive bias: for pursuer, aim for "shadow" positions around opponent by reducing dist faster.
        # For evader, aim to maximize dist while avoiding tight obstacle neighborhoods.
        nd = nearest_obst_dist(nx, ny)

        # Also penalize moves that "pass through" near obstacles (zigzag opponent often tries to slip around them).
        wall_pen = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            wall_pen = 1 if is_pursuer else -1

        if is_pursuer:
            # Strongly prefer decreasing distance; tie-breaker: keep away from obstacles unless they help you (very near -> bad).
            val = (-1000 * dist) + (10 * nd) + (-3 * wall_pen)
            # Micro-tie: prefer moves that also move toward being aligned with opponent (reduced squared manhattan).
            mdx = nx - ox
            if mdx < 0: mdx = -mdx
            mdy = ny - oy
            if mdy < 0: mdy = -mdy
            val -= 0.05 * (mdx + mdy)
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
        else:
            # Evader: maximize distance; avoid obstacles and edges only if it helps survive deterministically.
            val = (1000 * dist) + (8 * nd) + (2 * wall_pen)
            if val < best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]