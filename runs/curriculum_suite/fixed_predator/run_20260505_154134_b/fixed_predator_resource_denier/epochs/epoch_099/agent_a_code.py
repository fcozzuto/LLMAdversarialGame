def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    (sx, sy) = observation.get("self_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    (ox, oy) = observation.get("opponent_position", (0, 0))

    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, tx, ty)
            if best is None or d < best[0] or (d == best[0] and (nx + ny) < best[2]):
                best = (d, (dx, dy), nx + ny)
        return [best[1][0], best[1][1]]

    best_move = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Evaluate the best "resource denial" target from this next position
        best_val = None
        best_res_dist = None
        for (rx, ry) in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Higher means: resource closer to us than to opponent
            val = opp_d - self_d
            if best_val is None or val > best_val or (val == best_val and self_d < best_res_dist):
                best_val = val
                best_res_dist = self_d
        # Prefer higher denial gain; then closer to that chosen target; then deterministic tie-break
        score = (best_val, -best_res_dist, nx, ny)
        if best_move is None or score > best_move[0]:
            best_move = (score, (dx, dy))

    return [best_move[1][0], best_move[1][1]]