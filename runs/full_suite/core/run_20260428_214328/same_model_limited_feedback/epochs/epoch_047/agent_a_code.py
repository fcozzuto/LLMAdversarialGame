def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        best = None
        best_key = None
        for r in resources:
            rp = (r[0], r[1])
            sd = dist((sx, sy), rp)
            od = dist((ox, oy), rp)
            # Prefer resources we can reach sooner, and that opponent can't.
            key = (-(sd - od), sd, rp[0], rp[1])
            if best_key is None or key > best_key:
                best_key = key
                best = rp
        tx, ty = best
    else:
        tx, ty = (w // 2), (h // 2)

    desired = (0 if tx == sx else (1 if tx > sx else -1),
               0 if ty == sy else (1 if ty > sy else -1))
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            moves.append((dx, dy))

    def move_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        cur_t = dist((sx, sy), (tx, ty))
        new_t = dist((nx, ny), (tx, ty))
        prog = cur_t - new_t
        # Avoid stepping onto opponent if they are adjacent (slight penalty).
        adj_pen = 0
        if abs(nx - ox) <= 1 and abs(ny - oy) <= 1:
            adj_pen = -0.5
        # Prefer moves that align with desired direction, deterministically.
        align = - (abs(dx - desired[0]) + abs(dy - desired[1])) * 0.01
        # Mild obstacle/edge safety: keep away from edges if tied.
        edge = -((nx == 0 or nx == w - 1) + (ny == 0 or ny == h - 1)) * 0.01
        return prog + adj_pen + align + edge

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        val = move_score(dx, dy)
        # Deterministic tie-break: lexicographic on (dx, dy) after value.
        key = (val, -dx, -dy)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]