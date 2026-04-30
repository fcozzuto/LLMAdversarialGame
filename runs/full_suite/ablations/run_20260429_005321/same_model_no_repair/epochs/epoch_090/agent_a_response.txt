def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def near_obst(x, y):
        c = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + ddx, y + ddy) in obst:
                c += 1
        return c

    if resources:
        best_key = None
        best_move = (0, 0)
        for dx, dy, nx, ny in legal:
            # Choose a move that maximizes being closer than opponent to some resource,
            # while lightly preferring safer/less constrained squares.
            local_best = None
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer resources where we are closer; also account for opponent potentially getting there first.
                # Higher is better.
                val = (-ds + 0.85 * do) - 0.15 * ds - 0.02 * near_obst(nx, ny)
                if local_best is None or val > local_best:
                    local_best = val
            key = (-local_best, near_obst(nx, ny), cheb(nx, ny, sx, sy), dx, dy)  # deterministic tie-break
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: distance play. Run from opponent, but drift toward center while avoiding obstacles.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        dop = cheb(nx, ny, ox, oy)
        dcent = cheb(nx, ny, cx, cy)
        key = (-dop, dcent, near_obst(nx, ny), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]