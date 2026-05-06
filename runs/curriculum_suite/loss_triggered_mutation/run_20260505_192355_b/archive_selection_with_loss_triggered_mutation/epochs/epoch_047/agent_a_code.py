def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        score = 0
        # Intercept: if close to opponent, prioritize blocking by reducing distance
        opp_d = dist(nx, ny, ox, oy)
        if opp_d <= 2:
            score += 80 - 20 * opp_d

        # Resource contest: choose move that maximizes advantage over opponent
        if resources:
            best_adv = -10**18
            for (rx, ry) in resources:
                us = dist(nx, ny, rx, ry)
                op = dist(ox, oy, rx, ry)
                adv = op - us  # positive means we are closer
                # encourage reaching nearer resources sooner; discourage far contested losses
                val = 10 * adv - us
                if val > best_adv:
                    best_adv = val
            score += best_adv
        else:
            # No resources visible: drift toward center while keeping intercept pressure
            cx, cy = (w - 1) // 2, (h - 1) // 2
            score += -dist(nx, ny, cx, cy)

        # Avoid stepping into immediate obstacle-adjacent traps (lightweight robustness)
        for tx in (nx - 1, nx, nx + 1):
            for ty in (ny - 1, ny, ny + 1):
                if (tx, ty) in obst:
                    score -= 3

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move