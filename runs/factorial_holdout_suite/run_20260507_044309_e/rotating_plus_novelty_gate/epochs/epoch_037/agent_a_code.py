def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None; bestv = None
        for dx, dy, nx, ny in valid:
            v = dist(nx, ny, tx, ty)
            if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    best_move = None
    best_val = None
    for dx, dy, nx, ny in valid:
        best_for_move = None
        for rx, ry in resources:
            d_my = dist(nx, ny, rx, ry)
            d_op = dist(ox, oy, rx, ry)
            # Prefer being closer than opponent; prioritize not ceding easy pickups.
            val = d_my - 0.75 * d_op
            if best_for_move is None or val < best_for_move:
                best_for_move = val
        if best_val is None or best_for_move < best_val or (best_for_move == best_val and (dx, dy) < best_move):
            best_val = best_for_move
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]