def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def step(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return nx, ny
        return x, y

    if not resources:
        for dx, dy in moves:
            nx, ny = step(sx, sy, dx, dy)
            if (nx, ny) != (sx, sy):
                return [dx, dy]
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a target to beat the opponent: prefer cells where we are closer,
    # and deprioritize cells where the opponent is already faster.
    # Tie-break deterministically toward improving distance-to-center to avoid stalls.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_key = None
    for rx, ry in resources:
        sd = man((sx, sy), (rx, ry))
        od = man((ox, oy), (rx, ry))
        # Negative sd is good; positive od is bad.
        lead = sd - od  # smaller is better (we closer or opponent farther)
        center_bias = abs(rx - cx) + abs(ry - cy)
        key = (lead, sd, center_bias, rx, ry)
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key

    tx, ty = best

    # Evaluate one-move options with a local heuristic:
    # reduce distance to chosen target, and also reduce opponent's advantage.
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = step(sx, sy, dx, dy)
        sd2 = man((nx, ny), (tx, ty))
        od = man((ox, oy), (tx, ty))
        lead2 = sd2 - od
        # Slightly avoid moving away from target when stuck on equal lead.
        away = abs(nx - tx) + abs(ny - ty)
        mkey = (lead2, sd2, away, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]