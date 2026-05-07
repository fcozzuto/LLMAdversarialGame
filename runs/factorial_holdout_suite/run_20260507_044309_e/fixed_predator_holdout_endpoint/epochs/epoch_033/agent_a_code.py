def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        move_best = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive => we are closer
            if sd < od:
                val = 2 * adv - sd
            else:
                val = adv - 2 * sd  # discourage pursuing worse races
            if val > move_best:
                move_best = val

        # Small bias: avoid staying if equally good, and avoid moving away from all resources
        if move_best > best_val or (move_best == best_val and (dxm, dym) != (0, 0)):
            best_val = move_best
            best_move = [dxm, dym]

    if best_val == -10**18:
        return [0, 0]
    return best_move