def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Prefer resources we can reach no later than opponent; otherwise minimize our delay.
    # Add small deterministic bias to resources away from opponent's x to reduce sweep-row clashes.
    opp_x_bias = 0
    if ox < (w - 1) / 2.0:
        opp_x_bias = 1
    else:
        opp_x_bias = -1

    best = None
    best_key = None
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        reachable = 1 if d1 <= d2 else 0
        # tie-break: win chance first, then arrive sooner, then farther in row/col mismatch from opponent.
        margin = (d2 - d1)
        away = abs(rx - ox) + abs(ry - oy)
        xoff = opp_x_bias * (rx - ox)
        key = (reachable, margin, -d1, away, xoff)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    # If immediate diagonal target cell is an obstacle, fall back deterministically to axis step.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        if (sx + dx, sy) not in obstacles:
            return [dx, 0]
        if (sx, sy + dy) not in obstacles:
            return [0, dy]
        # otherwise stay
        return [0, 0]

    return [dx, dy]