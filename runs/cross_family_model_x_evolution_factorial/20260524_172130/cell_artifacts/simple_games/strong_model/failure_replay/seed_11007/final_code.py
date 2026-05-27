def choose_move(observation):
    def pos(v):
        return v if isinstance(v, (list, tuple)) and len(v) >= 2 else (0, 0)

    def add_points(keys):
        out = []
        for k in keys:
            for p in observation.get(k, []):
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    out.append((p[0], p[1]))
        return out

    w = observation.get("grid_width", observation.get("width", 0)) or 0
    h = observation.get("grid_height", observation.get("height", 0)) or 0
    sx, sy = pos(observation.get("self_position", (0, 0)))
    ox, oy = pos(observation.get("opponent_position", (sx, sy)))
    obstacles = set(add_points(("obstacles", "walls", "blocked", "rocks")))
    resources = add_points(("resources", "food", "pellets", "collectibles", "targets"))

    if not resources:
        best = (0, 0)
        bests = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if abs(dx) + abs(dy) != 1:
                    continue
                nx, ny = sx + dx, sy + dy
                if w and (nx < 0 or nx >= w) or h and (ny < 0 or ny >= h) or (nx, ny) in obstacles:
                    continue
                s = -abs(nx - ox) - abs(ny - oy)
                if s > bests:
                    bests, best = s, (dx, dy)
        return [best[0], best[1]]

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if w and (nx < 0 or nx >= w) or h and (ny < 0 or ny >= h) or (nx, ny) in obstacles:
            return -10**9
        dself = min(abs(nx - x) + abs(ny - y) for x, y in resources)
        dop = min(abs(nx - ox) + abs(ny - oy), 9)
        return -3 * dself + dop - abs(dx) - abs(dy)

    best = (0, 0)
    bests = -10**9
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        s = score_move(dx, dy)
        if s > bests:
            bests, best = s, (dx, dy)
    return [best[0], best[1]]
