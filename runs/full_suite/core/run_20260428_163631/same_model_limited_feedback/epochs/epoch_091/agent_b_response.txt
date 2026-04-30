def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    def step_ok(nx, ny):
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            return False
        if (nx, ny) in obstacles:
            return False
        return True

    if resources:
        best = None
        for rx, ry in resources:
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            key = (ds - do, ds, abs(rx - ox) + abs(ry - oy))
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_score = None
    curd = dist((sx, sy), (tx, ty))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            continue
        if nx == ox and ny == oy:
            continue
        nd = dist((nx, ny), (tx, ty))
        oppd = dist((ox, oy), (tx, ty))
        gain = (curd - nd)  # positive if closer
        behind = (nd - oppd)  # lower if we are closer than opponent
        score = (behind, -gain, abs(nx - tx) + abs(ny - ty))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]