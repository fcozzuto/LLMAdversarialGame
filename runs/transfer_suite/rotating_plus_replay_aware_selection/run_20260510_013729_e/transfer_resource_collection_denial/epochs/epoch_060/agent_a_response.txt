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

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    resources_sorted = sorted(resources, key=lambda p: (p[0] * 8 + p[1], p[0], p[1]))

    bestv = -10**18
    bestd = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        best_for_cell = -10**18
        for rx, ry in resources_sorted:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            capture = 3.0 if (nx, ny) == (rx, ry) else 0.0
            lead = do - ds  # bigger => we can deny / reach first
            val = capture + 2.2 * lead - 0.35 * ds + 0.03 * cheb(nx, ny, ox, oy)
            if val > best_for_cell:
                best_for_cell = val
        # Small tie-break: prefer progressing closer to best resource
        tie = -cheb(nx, ny, resources_sorted[0][0], resources_sorted[0][1]) * 1e-6
        v = best_for_cell + tie

        if v > bestv:
            bestv = v
            bestd = (dx, dy)

    return [int(bestd[0]), int(bestd[1])]