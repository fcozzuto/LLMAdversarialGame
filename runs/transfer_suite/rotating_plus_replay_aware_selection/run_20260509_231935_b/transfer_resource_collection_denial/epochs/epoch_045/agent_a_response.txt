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
        val = 0
        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            sd = dist8(nx, ny, rx, ry)
            od = dist8(ox, oy, rx, ry)
            # Prefer resources where we are (or stay) closer than opponent
            # and prefer being close overall.
            val_r = (od - sd) * 6 - sd
            # Encourage grabbing nearer resources sooner (diminishing returns)
            if sd == 0:
                val_r += 1000
            elif sd == 1:
                val_r += 120
            val += val_r
        # Small tie-break: move that reduces our distance to the best resource target
        # (computed approximately by comparing max over targets)
        best_sd = None
        best_gap = -10**18
        for rx, ry in res:
            sd = dist8(nx, ny, rx, ry)
            if sd < (best_sd if best_sd is not None else 10**9):
                best_sd = sd
            od = dist8(ox, oy, rx, ry)
            gap = od - sd
            if gap > best_gap:
                best_gap = gap
        val += best_gap * 2 - (best_sd if best_sd is not None else 0)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move