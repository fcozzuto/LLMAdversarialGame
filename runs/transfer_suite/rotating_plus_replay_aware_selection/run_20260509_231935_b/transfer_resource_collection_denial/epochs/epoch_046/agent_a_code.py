def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    res = {(p[0], p[1]) for p in resources}
    obs = {(p[0], p[1]) for p in obstacles}
    if not resources:
        return [0, 0]

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Immediate pickup
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res and (nx, ny) not in obs:
            return [dx, dy]

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        best_for_cell = -10**18
        # Favor resources where we are closer than opponent; break ties toward nearer.
        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            my_d = dist8(nx, ny, rx, ry)
            opp_d = dist8(ox, oy, rx, ry)
            if my_d == 0:
                val = 10**12
            else:
                val = (opp_d - my_d) * 1000 - my_d
            if val > best_for_cell:
                best_for_cell = val

        # Slight preference to move generally toward the opponent side (to avoid stalling).
        orient_bias = 0
        if w == 8 and h == 8:
            orient_bias = (nx - sx) * 0.5 + (ny - sy) * 0.25
        val = best_for_cell + orient_bias
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]