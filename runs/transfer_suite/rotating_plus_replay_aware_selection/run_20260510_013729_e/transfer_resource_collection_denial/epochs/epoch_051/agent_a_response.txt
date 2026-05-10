def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    rs = sorted(resources, key=lambda p: (p[0] * 16 + p[1], p[0], p[1]))
    cell_targets = rs if len(rs) < 10 else rs[:10]

    best_mv = [0, 0]
    best_val = -10**18

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = 0.0
        if (nx, ny) in obst:
            val -= 5.0
        # main objective: maximize expected gain by being closer than opponent
        for rx, ry in cell_targets:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            cap = 3.6 if (nx, ny) == (rx, ry) else 0.0
            lead = do - ds  # positive means we are closer in chebyshev distance
            # If we can capture this turn or be the clearer next claim, prioritize.
            val += cap
            val += 2.4 * lead
            val -= 0.26 * ds
            val += 0.06 * cheb(nx, ny, ox, oy)  # stay away from opponent when tie
        # secondary: keep moving toward the single best plausible target
        if cell_targets:
            rx, ry = cell_targets[0]
            val -= 0.02 * cheb(nx, ny, rx, ry)

        if val > best_val:
            best_val = val
            best_mv = [dx, dy]
    return best_mv