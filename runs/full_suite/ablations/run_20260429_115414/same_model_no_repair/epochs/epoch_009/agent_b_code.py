def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a target deterministically: prefer resources where we are closer than the opponent.
    if resources:
        best_key = None
        tx, ty = sx, sy
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Primary: maximize advantage (opponent distance - my distance).
            # Secondary: minimize my distance.
            # Tertiary: prefer cells closer to our side center for later routing stability.
            centerx, centery = (w - 1) // 2, (h - 1) // 2
            key = (opd - myd, -myd, -(abs(rx - centerx) + abs(ry - centery)), -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                tx, ty = rx, ry
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = [0, 0]
    best_val = None
    base_opd = cheb(ox, oy, tx, ty)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_to_t = cheb(nx, ny, tx, ty)
        op_to_t = cheb(ox, oy, tx, ty)
        # Score: move toward target; if we can't improve, still pick move that maximizes advantage.
        adv = op_to_t - my_to_t
        # Keep away from opponent to reduce their future access.
        my_to_o = cheb(nx, ny, ox, oy)
        # If obstacle forces staying, keep deterministic by tie-breaking on deltas.
        val = (adv, -my_to_t, my_to_o, -abs(nx - (w - 1)), -abs(ny - (h - 1)), -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if inb(sx + best_move[0], sy + best_move[1]) else [0, 0]