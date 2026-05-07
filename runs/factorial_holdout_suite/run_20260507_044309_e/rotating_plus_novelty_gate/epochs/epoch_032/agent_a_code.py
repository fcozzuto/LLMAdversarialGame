def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx + dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if resources:
        best_moves = []
        for dx, dy, nx, ny in valid:
            best_adv = -10**9
            best_time = 10**9
            for rx, ry in resources:
                sd = dist(nx, ny, rx, ry)
                od = dist(ox, oy, rx, ry)
                adv = od - sd  # positive means we arrive no later than opponent (deny/claim)
                t = sd
                if adv > best_adv or (adv == best_adv and (t < best_time)):
                    best_adv = adv
                    best_time = t
            # Prefer immediate collection; tie-break toward earlier arrival then toward center.
            key = (best_adv, -best_time, -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)))
            best_moves.append((key, [dx, dy]))
        best_moves.sort(key=lambda x: (x[0][0], x[0][1], x[0][2]), reverse=True)
        # Additionally, if standing next to a resource, take it deterministically.
        for dx, dy, nx, ny in valid:
            for rx, ry in resources:
                if nx == rx and ny == ry:
                    return [dx, dy]
        return best_moves[0][1]

    # No visible resources: drift to center while avoiding obstacles.
    cx = (w - 1) / 2; cy = (h - 1) / 2
    best = None
    best_val = 10**18
    for dx, dy, nx, ny in valid:
        val = abs(nx - cx) + abs(ny - cy)
        if val < best_val:
            best_val = val; best = [dx, dy]
    return best if best is not None else [0, 0]