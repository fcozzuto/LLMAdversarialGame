def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obstacle_set = {(x, y) for x, y in obstacles}

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose a resource where we have the strongest arrival advantage (and then closest).
    best = resources[0]
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds, -ds, -(rx * 8 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # If target cell becomes unreachable due to obstacles blocking a direct neighbor, we still move greedily.
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacle_set:
            continue

        # Primary: minimize chebyshev distance to target.
        d1 = cheb(nx, ny, tx, ty)
        # Secondary: prevent stepping "into danger" near obstacles (soft penalty).
        danger = 0
        for ax, ay in obstacles:
            dd = cheb(nx, ny, ax, ay)
            if dd == 0:
                danger += 10
            elif dd == 1:
                danger += 2
        # Also consider improving our arrival advantage immediately.
        cur_self = cheb(nx, ny, tx, ty)
        cur_opp = cheb(ox, oy, tx, ty)
        adv = cur_opp - cur_self
        score = (adv, -cur_self, -(danger), -(nx * 8 + ny))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]