def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    in_bounds = lambda x, y: 0 <= x < w and 0 <= y < h

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]

    if resources:
        opp_d = dist2((ox, oy), (sx, sy))
        # pick a target resource that is good for us and less accessible for opponent
        best = None
        for rx, ry in resources:
            ds = dist2((sx, sy), (rx, ry))
            do = dist2((ox, oy), (rx, ry))
            score = ds - 0.35 * do
            if best is None or score < best[0] or (score == best[0] and (do > best[2])):
                best = (score, (rx, ry), do)
        tx, ty = best[1]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # choose move that most improves distance to target; mild repulsion from opponent
    best_move = None
    best_val = None
    for dx, dy, nx, ny in valid:
        dtn = dist2((nx, ny), (tx, ty))
        dto = dist2((nx, ny), (ox, oy))
        # deterministic tie-break: prefer smaller dtn, then larger dto, then lexicographic dx,dy
        val = (dtn, -dto, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]