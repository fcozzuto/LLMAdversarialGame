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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    if not resources:
        # drift toward center if no resources listed
        cx, cy = w // 2, h // 2
        best_d = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, cx, cy)
            if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_move):
                best_d = d
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer moves that get us significantly closer to a resource than the opponent currently is.
        # Also keep a small tie-breaker toward immediate proximity.
        local_best = None
        for rx, ry in resources:
            our = cheb(nx, ny, rx, ry)
            opp = cheb(ox, oy, rx, ry)
            # Higher opponent distance -> better; closer to resource -> better
            val = our * 2 - opp
            if local_best is None or val < local_best:
                local_best = val
        # Small deterministic tie-breaker: prefer smaller our distance to the best resource
        tie_d = cheb(nx, ny, resources[0][0], resources[0][1])
        for rx, ry in resources[1:]:
            d = cheb(nx, ny, rx, ry)
            if d < tie_d:
                tie_d = d
        if best_val is None or local_best < best_val or (local_best == best_val and (tie_d < 0 or tie_d < cheb(sx + best_move[0], sy + best_move[1], resources[0][0], resources[0][1]) or (tie_d == 0 and (dx, dy) < best_move))):
            best_val = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]