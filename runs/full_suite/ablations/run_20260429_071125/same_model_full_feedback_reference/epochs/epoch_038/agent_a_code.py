def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [int(dx), int(dy)]
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    # Strategy: for each move, evaluate best "contested" resource (close for us, far for opponent),
    # then add a secondary term to keep away from opponent.
    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            me = (nx, ny)
            my_best = None
            for rx, ry in resources:
                r = (rx, ry)
                ds = dist(me, r)
                do = dist((ox, oy), r)
                # Prefer resources we can reach sooner than opponent; heavily penalize cases opponent is closer.
                val = (ds - do, ds, -do, rx, ry)
                if my_best is None or val < my_best:
                    my_best = val
            # opponent-avoidance scaled to reduce collisions and stealing
            opp_dist = dist(me, (ox, oy))
            # Convert tuple to numeric with deterministic weights
            d_diff, ds, n_do, _, _ = my_best
            score = (d_diff * 1000) + (opp_dist * 3) - (ds * 2) + (n_do // 1)
            if best_val is None or score > best_val:
                best_val = score
                best_move = (dx, dy)
    else:
        # No visible resources: drift toward center while keeping distance from opponent.
        cx, cy = w // 2, h // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_center = dist((nx, ny), (cx, cy))
            d_opp = dist((nx, ny), (ox, oy))
            score = (d_opp * 2) - d_center
            if best_val is None or score > best_val:
                best_val = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]