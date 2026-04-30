def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_target(rx, ry):
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Primary: we are closer than opponent; Secondary: closeness; Tertiary: value proxy (distance-from-corners)
        return (do - ds) * 1000 - ds * 3 + (rx + ry)

    # Pick best target by deterministic ordering of ties
    best = None
    best_sc = None
    for rx, ry in resources:
        sc = score_target(rx, ry)
        if best is None or sc > best_sc or (sc == best_sc and (rx, ry) < best):
            best_sc = sc
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Greedy towards target with local avoidance; deterministic tie-break.
    best_move = (0, 0)
    best_cost = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Prefer reducing our distance; if equal, prefer also reducing opponent distance to same target (denying)
        opp_d = cheb(ox, oy, tx, ty)
        my_adv = d - cheb(nx, ny, tx, ty)  # always 0; keep structure simple and deterministic
        cost = d * 10 - (opp_d - cheb(ox, oy, tx, ty)) + 0 * my_adv
        if best_cost is None or cost < best_cost or (cost == best_cost and (dx, dy) < best_move):
            best_cost = cost
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]