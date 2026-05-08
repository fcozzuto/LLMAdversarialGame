def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    px, py = observation.get("opponent_position", [0, 0])
    sx, sy, px, py = int(sx), int(sy), int(px), int(py)
    self_role = (observation.get("self_role", "") or "").lower()
    obstacles = observation.get("obstacles", []) or []
    ox = {(int(a), int(b)) for a, b in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return in_bounds(x, y) and (x, y) not in ox

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if free(nx, ny):
                c += 1
        return c

    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role)
    if self_role == "" and self_role == "":
        is_evader = False

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_val = None

    # Deterministic tie-breaker by move order already.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, px, py)
        fn = free_neighbors(nx, ny)
        # Favor staying away from corners (for evader) or cutting distance (for pursuer).
        dist_center = abs(nx - cx) + abs(ny - cy)
        if is_evader:
            val = (d, fn, -dist_center)
        else:
            val = (-d, fn, dist_center)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]