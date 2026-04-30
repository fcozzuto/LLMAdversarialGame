def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def clamp(px, py):
        if px < 0: px = 0
        if py < 0: py = 0
        if px >= w: px = w - 1
        if py >= h: py = h - 1
        return px, py

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy  # Chebyshev for 8-dir movement

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def best_target_score(px, py):
        best_margin = None
        best_margin_val = None
        best_near = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist((px, py), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            margin = do - ds  # positive means we are closer
            if best_margin is None or margin > best_margin_val:
                best_margin, best_margin_val = (rx, ry), margin
            if best_near is None or ds < dist((px, py), best_near):
                best_near = (rx, ry)
        if best_margin_val is not None and best_margin_val > 0:
            tx, ty = best_margin
        else:
            tx, ty = best_near if best_near is not None else (px, py)
        return dist((px, py), (tx, ty)), dist((px, py), (ox, oy))

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = clamp(x + dx, y + dy)
        if (nx, ny) in obstacles:
            nx, ny = x, y
        to_res, to_opp = best_target_score(nx, ny)
        # Prioritize being first to a resource; then keep distance from opponent.
        val = (-2.4 * to_res) + (0.9 * to_opp)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]