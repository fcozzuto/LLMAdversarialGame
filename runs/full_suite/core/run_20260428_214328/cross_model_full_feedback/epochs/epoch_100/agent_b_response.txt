def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def dist_cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    self_pos = (sx, sy)
    opp_pos = (ox, oy)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    # Helper: stay away from immediate collision with obstacle or opponent
    def blocked(px, py):
        return (px, py) in obst or not in_bounds(px, py)

    # Evaluate candidate moves with simple deterministic scoring
    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obst:
            # invalid; skip to keep in place as fallback
            if dx == 0 and dy == 0:
                pass
            else:
                continue
        # basic score: prefer getting closer to nearest resource and staying near but not too close to opponent
        score = 0

        # distance to closest resource
        if resources:
            score -= min(dist_cheb((nx, ny), r) for r in resources)

        # distance to opponent: want to avoid direct collision, but also pressure
        d_opp = dist_cheb((nx, ny), opp_pos)
        if d_opp == 0:
            score -= 100  # avoid landing on opponent
        else:
            score += d_opp  # prefer staying away

        # prefer staying in bounds and not stepping into obstacles
        if (nx, ny) in obst:
            score -= 50

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If by any chance best_move leads into obstacle or out of bounds, fallback to staying
    fx, fy = sx + best_move[0], sy + best_move[1]
    if not in_bounds(fx, fy) or (fx, fy) in obst:
        return [0, 0]
    return [best_move[0], best_move[1]]