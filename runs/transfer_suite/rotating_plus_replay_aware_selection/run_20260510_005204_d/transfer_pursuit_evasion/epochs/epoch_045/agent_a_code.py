def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    mode_away = ("evader" in self_role) or ("runner" in self_role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh8 = moves

    def open_neighbors(x, y):
        c = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                c += 1
        return c

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if mode_away:
        # Prefer moves that keep distance and steer away from the closest corner to the opponent
        oc = min(corners, key=lambda t: abs(t[0] - ox) + abs(t[1] - oy))
        corner_pen = lambda x, y: abs(x - oc[0]) + abs(y - oc[1])
    else:
        # Prefer moves that push toward the closest corner to the opponent
        oc = min(corners, key=lambda t: abs(t[0] - ox) + abs(t[1] - oy))
        corner_pen = lambda x, y: -abs(x - oc[0]) - abs(y - oc[1])

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d = abs(nx - ox) + abs(ny - oy)
        open_n = open_neighbors(nx, ny)
        # Avoid stepping into tight traps; deterministic tie-breakers include dx,dy
        trap = 0
        if open_n <= 2:
            trap = 1
        # If evading, also bias toward staying on the "far side" of the opponent relative to board center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        sgnx = 1 if nx - cx >= 0 else -1
        sgny = 1 if ny - cy >= 0 else -1
        side_bias = (1 if (ox - cx) * sgnx >= 0 else -1) + (1 if (oy - cy) * sgny >= 0 else -1)

        if mode_away:
            key = (-(d), -corner_pen(nx, ny), trap, -open_n, side_bias, dx, dy)
        else:
            key = (d, -corner_pen(nx, ny), trap, -open_n, -side_bias, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]