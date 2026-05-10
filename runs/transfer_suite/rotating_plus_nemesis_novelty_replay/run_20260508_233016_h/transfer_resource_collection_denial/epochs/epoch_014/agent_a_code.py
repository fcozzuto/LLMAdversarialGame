def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if any((rx, ry) == (sx, sy) for rx, ry in resources):
        return [0, 0]

    best_dx, best_dy = 0, 0
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        # Choose move that maximizes our "next-step advantage" on the single best-denied resource.
        local_best_adv = None
        local_best_selfd = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive => we are closer (or opponent farther)
            if local_best_adv is None or adv > local_best_adv or (adv == local_best_adv and sd < local_best_selfd):
                local_best_adv = adv
                local_best_selfd = sd
        # Global tie-break: prefer larger advantage, then closer to that target, then progress toward opponent (denial).
        if best_val is None:
            best_val = (local_best_adv, -local_best_selfd, -man(sx, sy, ox, oy))
            best_dx, best_dy = dx, dy
        else:
            cand = (local_best_adv, -local_best_selfd, -man(sx + dx, sy + dy, ox, oy))
            if cand > best_val:
                best_val = cand
                best_dx, best_dy = dx, dy

    return [best_dx, best_dy]