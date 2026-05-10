def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1))

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            val = d8(nx, ny, tx, ty)
            cand = (val, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]

    k = 1.05
    best_val = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        nearest_own = 10**9
        nearest_opp = 10**9
        for rx, ry in resources:
            if (rx, ry) == (nx, ny):
                nearest_own = 0
                nearest_opp = 0
                break
            du = d8(nx, ny, rx, ry)
            do = d8(ox, oy, rx, ry)
            if du < nearest_own:
                nearest_own = du
            if do < nearest_opp:
                nearest_opp = do

        # Prefer reducing our distance while also making resources less reachable for opponent.
        # Small tie-break biases toward closer to opponent's corner direction.
        corner_bias = (d8(nx, ny, w - 1, h - 1) - d8(ox, oy, w - 1, h - 1)) * 0.02
        val = nearest_own - k * nearest_opp + corner_bias

        if best_val is None or val < best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]

    return best_move