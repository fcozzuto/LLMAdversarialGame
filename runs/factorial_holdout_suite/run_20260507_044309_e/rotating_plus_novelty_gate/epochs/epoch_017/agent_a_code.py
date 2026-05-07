def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = {(p[0], p[1]) for p in observation.get("obstacles", [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Opponent likely targets the resource it is closest to.
    opp_best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d = man(ox, oy, rx, ry)
        if opp_best is None or d < opp_best[0]:
            opp_best = (d, rx, ry)
    opp_target = (opp_best[1], opp_best[2]) if opp_best else None

    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = 0.0
        # Prefer moves that secure resources before opponent (positive margin), and block opponent's likely target.
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            margin = opp_d - our_d  # >0 means we are closer
            if our_d == 0:
                score += 10000.0 + opp_d * 0.1
            elif margin > 0:
                score += 10.0 * margin - 0.5 * our_d
            else:
                score += 0.2 * margin  # mild penalty
        if opp_target:
            tx, ty = opp_target
            # Interception: reduce distance to opponent's likely target, but only if we can plausibly contest.
            our_dt = man(nx, ny, tx, ty)
            opp_dt = man(ox, oy, tx, ty)
            if our_dt <= opp_dt:
                score += 30.0 * (opp_dt - our_dt) - 0.2 * our_dt
            else:
                score -= 2.0 * (our_dt - opp_dt)
        # Tie-break deterministically toward staying closer to overall resources.
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]