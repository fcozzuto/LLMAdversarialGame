def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def mhd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Prefer resources around opponent's current y (row-sweep pressure), and where we are closer.
    best = None
    best_val = -10**18
    for rx, ry in resources:
        self_d = mhd(sx, sy, rx, ry)
        opp_d = mhd(ox, oy, rx, ry)
        row_dist = abs(ry - oy)
        row_bias = 14 - 3 * row_dist  # strongest on opponent's current row
        # If we can reach much sooner, prioritize; otherwise still try to deny if near.
        val = (opp_d - self_d) + row_bias - 0.05 * self_d
        if val > best_val:
            best_val = val
            best = (rx, ry)

    rx, ry = best

    def step_options(x, y):
        opts = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                    opts.append((dx, dy, nx, ny))
        if not opts:
            opts = [(0, 0, x, y)]
        return opts

    # Greedy toward target; if blocked, pick best alternative deterministically.
    dxg = 0
    if rx > sx: dxg = 1
    elif rx < sx: dxg = -1
    dyg = 0
    if ry > sy: dyg = 1
    elif ry < sy: dyg = -1

    preferred = None
    for dx, dy, nx, ny in step_options(sx, sy):
        if dx == dxg and dy == dyg:
            preferred = (dx, dy, nx, ny)
            break
    if preferred is not None:
        return [int(preferred[0]), int(preferred[1])]

    # Otherwise choose among legal moves the one improving our advantage toward the best resource.
    best_local = None
    best_local_val = -10**18
    for dx, dy, nx, ny in step_options(sx, sy):
        self_d = mhd(nx, ny, rx, ry)
        opp_d = mhd(ox, oy, rx, ry)
        row_dist = abs(ry - oy)
        row_bias = 14 - 3 * row_dist
        val = (opp_d - self_d) + row_bias - 0.05 * self_d
        if val > best_local_val:
            best_local_val = val
            best_local = (dx, dy)
    return [int(best_local[0]), int(best_local[1])]