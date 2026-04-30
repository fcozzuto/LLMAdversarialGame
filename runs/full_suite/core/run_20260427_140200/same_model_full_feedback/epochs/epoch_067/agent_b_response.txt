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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If resources exist: maximize (opponent_time - self_time) for the best resource after this move.
    # Else: drift deterministically toward center.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            local_best = -10**18
            local_res = None
            for rx, ry in resources:
                opp_t = cheb(ox, oy, rx, ry)
                self_t = cheb(nx, ny, rx, ry)
                adv = opp_t - self_t  # positive means we can arrive earlier
                # Tie-breaker favors nearer resources and lexicographically smaller coords
                val = adv * 1000 - self_t
                if val > local_best or (val == local_best and ((rx, ry) < local_res)):
                    local_best = val
                    local_res = (rx, ry)
            # Secondary tie-break: prefer staying closer to chosen resource.
            rx, ry = local_res
            score = local_best - cheb(nx, ny, rx, ry)
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            score = -cheb(nx, ny, cx, cy)
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]