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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        center_bias = cheb(sx, sy, w // 2, h // 2)
        best = None
        best_score = -10**18
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources we can win (d_me smaller), otherwise still pick the most contestable.
            win_margin = d_op - d_me  # higher is better for us
            score = win_margin * 1000 - d_me * 3
            # If we are behind overall, steer to resources with non-negative margin.
            if d_op < d_me:
                score -= 1200  # harshly penalize losing targets
            # Tie-break: slight preference toward closer to center to avoid edge traps.
            score -= (center_bias * 0.01)
            if score > best_score:
                best_score = score
                best = (rx, ry)
        tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dist_to = cheb(nx, ny, tx, ty)
        dist_from_opp = cheb(nx, ny, ox, oy)
        # Contention pressure: if opponent is also targeting near us, increase separation.
        opp_dist_to = cheb(ox, oy, tx, ty)
        my_dist_now = cheb(sx, sy, tx, ty)
        opp_is_hot = 1 if opp_dist_to <= my_dist_now else 0
        val = -dist_to * 10 + dist_from_opp * (3 + opp_is_hot * 2)
        # If we can match/opponent is closer, prefer moves that keep win margin non-decreasing.
        if not resources:
            pass
        else:
            my_now = cheb(sx, sy, tx, ty)
            opp_now = cheb(ox, oy, tx, ty)
            if opp_now >= my_now:
                val += (opp_now - dist_to) * 5
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]