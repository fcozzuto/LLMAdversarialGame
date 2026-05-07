def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    res_set = set((int(r[0]), int(r[1])) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2)
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    # If we can take a resource now, do it.
    if (sx, sy) in res_set:
        return [0, 0]

    best = None
    best_val = None
    for dx, dy, nx, ny in legal:
        # Choose the best target resource for this move, but penalize if opponent can contest earlier.
        best_margin = None
        best_dist_self = None
        for rx, ry in res_set:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            margin = od - sd  # positive => we reach earlier
            if best_margin is None or margin > best_margin or (margin == best_margin and sd < best_dist_self):
                best_margin = margin
                best_dist_self = sd
        # Encourage proximity and discourage getting stuck near contested resources.
        val = best_margin * 100 - best_dist_self
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]