def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a "contested" target: where opponent is closer, but we are not too far.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # want high (od - sd): we are closer; but if none, prioritize stealing where opponent leads modestly.
        lead = od - sd
        steal = (od <= sd + 2)
        # Prefer resources closer to center a bit to avoid corner traps.
        center_bias = -(abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)) * 0.01
        key = (steal, lead, -sd, center_bias, -rx, -ry)
        if best is None or key > best:
            best = key
            target = (rx, ry)

    tx, ty = target

    # Choose step that improves our reach to target while increasing opponent's difficulty.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            # invalid move will be handled by engine; but we avoid it to keep deterministic optimality
            continue

        self_next = man(nx, ny, tx, ty)
        opp_next = man(ox, oy, tx, ty)
        # approximate "blocking": prefer reducing our distance more than opponent (intercept pressure)
        pressure = (opp_next - self_next)

        # obstacle aversion: penalize moving adjacent to obstacles to reduce getting stuck
        adj_obs = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax2, ay2 = nx + adx, ny + ady
                if 0 <= ax2 < w and 0 <= ay2 < h and (ax2, ay2) in obstacles:
                    adj_obs += 1
        key = (pressure, -self_next, -adj_obs, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    # If all candidate steps were invalid (surrounded by obstacles), stay.
    return [int(best_move[0]), int(best_move[1])]