def choose_move(observation):
    x0, y0 = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles", [])
    obst = set((a, b) for a, b in obstacles)
    resources = observation.get("resources", [])
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def best_resource_score(nx, ny):
        if not resources:
            return 0, 999999
        best = None
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            sc = (do - ds) * 5 - ds
            if best is None or sc > best[0] or (sc == best[0] and ds < best[1]):
                best = (sc, ds)
        return best[0], best[1]

    best_move = None
    for dx, dy in deltas:
        nx, ny = x0 + dx, y0 + dy
        if not in_bounds(nx, ny) or (nx, ny) in obst:
            continue
        if (nx, ny) == (ox, oy):
            sc = -10**9
        else:
            sc1, _ = best_resource_score(nx, ny)
            sc = sc1
            if not resources:
                cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
                sc = -((nx - cx) ** 2 + (ny - cy) ** 2) + 0.5 * (md(nx, ny, ox, oy))
        if best_move is None or sc > best_move[0] or (sc == best_move[0] and (nx, ny) < best_move[1]):
            best_move = (sc, (nx, ny), dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[2], best_move[3]]