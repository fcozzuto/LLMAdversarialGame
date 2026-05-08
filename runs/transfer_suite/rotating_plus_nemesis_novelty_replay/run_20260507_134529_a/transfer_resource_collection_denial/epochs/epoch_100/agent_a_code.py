def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        # Deterministic "hold but pressure": minimize my distance to opponent while not moving toward obstacles risk already handled.
        best = None
        for dx, dy, nx, ny in moves:
            d = man(nx, ny, ox, oy)
            if best is None or d < best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Prefer resources where we are likely to arrive earlier than opponent; tie-break by proximity and local density.
    best_val = None
    best_move = (0, 0)
    for dx, dy, nx, ny in moves:
        # Look one step ahead: evaluate same objective from candidate position.
        local_best = None
        for rx, ry in resources:
            myt = man(nx, ny, rx, ry)
            ot = man(ox, oy, rx, ry)
            lead = ot - myt  # positive means we arrive earlier or more tightly
            # density: count nearby resources (within Chebyshev radius 1 or 2) to reduce getting "stuck"
            density = 0
            for px, py in resources:
                if px == rx and py == ry:
                    continue
                if max(abs(px - rx), abs(py - ry)) <= 2:
                    density += 1
            # Val: prioritize lead, then closer, then density, then deterministic.
            val = (lead, -man(nx, ny, rx, ry), density, -rx, -ry)
            if local_best is None or val > local_best[0]:
                local_best = (val, myt)
        if local_best is None:
            continue
        if best_val is None or local_best[0] > best_val[0] or (local_best[0] == best_val[0] and (dx, dy) < best_move):
            best_val = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]