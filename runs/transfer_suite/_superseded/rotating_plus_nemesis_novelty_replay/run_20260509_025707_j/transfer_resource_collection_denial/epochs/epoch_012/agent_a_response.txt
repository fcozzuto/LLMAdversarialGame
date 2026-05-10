def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    if not resources:
        return [0, 0]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate the best resource we could reach next, racing opponent.
        best_adv = None
        best_selfd = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            key = (adv, -sd)  # maximize advantage, then closer
            if best_adv is None or key > (best_adv, best_selfd):
                best_adv = adv
                best_selfd = -sd
        # Additional tie-break: prefer moves that keep closer to the overall closest resource
        if best_adv is None:
            continue
        cur_best = man(sx, sy, resources[0][0], resources[0][1])
        for rx, ry in resources:
            d = man(sx, sy, rx, ry)
            if d < cur_best:
                cur_best = d
        next_closest = None
        for rx, ry in resources:
            d = man(nx, ny, rx, ry)
            if next_closest is None or d < next_closest:
                next_closest = d
        key = (best_adv, best_selfd, -(next_closest - cur_best), -((nx + ny) & 1))
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return best_move