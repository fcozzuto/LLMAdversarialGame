def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Pick a target deterministically using a contested-race heuristic.
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        gap = do - ds  # positive means we reach first (in time units)
        # If we're not ahead, prioritize minimizing the worst time to reduce opponent denial chances.
        worst = ds if ds >= do else do
        key = (gap, -worst, -ds, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Choose the move that most reduces our time to the chosen target, with a small tie-break to also
    # slightly reduce opponent time to that same target (helps contesting resource_denier behavior).
    best_move = None
    best_val = None
    for dx, dy, nx, ny in legal:
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        val = (-(ns), -(no - no), ns + 0, -abs(nx - tx) - abs(ny - ty), -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]