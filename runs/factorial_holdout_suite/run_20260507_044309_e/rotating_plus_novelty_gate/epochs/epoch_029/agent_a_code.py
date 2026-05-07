def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx + dy

    # If adjacent to a resource, take it immediately
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            for rx, ry in resources:
                if nx == rx and ny == ry:
                    return [dx, dy]

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    # One-step lookahead: choose move maximizing best "lead margin" over opponent
    # margin = (opp_dist - self_dist); tie-break: closer to resource, then toward center-ish.
    best_move = None
    best_key = None
    for dx, dy, nx, ny in valid:
        max_margin = -10**9
        best_dist = 10**9
        for rx, ry in resources:
            if not inb(rx, ry):
                continue
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            margin = od - sd
            if margin > max_margin:
                max_margin = margin
                best_dist = sd
            elif margin == max_margin and sd < best_dist:
                best_dist = sd
        center_x = (w - 1) / 2.0; center_y = (h - 1) / 2.0
        cdist = abs(nx - center_x) + abs(ny - center_y)
        # Prefer winning leads; if no leads, minimize opponent reach advantage; encourage progress.
        key = (max_margin, -best_dist, -cdist)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]