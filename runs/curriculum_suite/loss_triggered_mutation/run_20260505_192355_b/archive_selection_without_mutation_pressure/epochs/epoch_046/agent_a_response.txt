def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose best contested target using Chebyshev distance (diagonals cost 1 turn).
    best_r = None
    best_adv = -10**9
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        adv = dist(ox, oy, rx, ry) - dist(sx, sy, rx, ry)
        if adv > best_adv:
            best_adv = adv
            best_r = (rx, ry)

    # Estimate opponent likely target (nearest resource to opponent).
    opp_target = None
    opp_best_d = 10**9
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        d = dist(ox, oy, rx, ry)
        if d < opp_best_d:
            opp_best_d = d
            opp_target = (rx, ry)

    def move_value(nx, ny, mode_target, mode_adv):
        tx, ty = mode_target
        myd = dist(nx, ny, tx, ty)
        oppd = dist(ox, oy, tx, ty)
        # If we are pursuing a contested target, maximize advantage; otherwise, minimize our distance to the opponent's target.
        if mode_adv:
            return (oppd - myd) * 1000 - myd
        else:
            return -myd * 1000 + (oppd - myd)

    pursuing = best_adv >= 0 and best_r is not None

    if pursuing:
        target = best_r
        mode_adv = True
    else:
        target = opp_target
        mode_adv = False

    best_move = (0, 0)
    best_val = -10**18
    # Deterministic tie-break by move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        val = move_value(nx, ny, target, mode_adv)
        # Small additional bias: keep improving relative to opponent when possible.
        if pursuing:
            val += (dist(ox, oy, sx, sy) - dist(ox, oy, nx, ny))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]