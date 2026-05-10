def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set((int(x), int(y)) for x, y in obstacles if isinstance(x, (int, float)) and isinstance(y, (int, float)) and len([x, y]) >= 2)

    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))

    cx, cy = w // 2, h // 2
    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def score(nx, ny):
        if (nx, ny) in obs:
            return -10**9
        # Prefer expanding into unclaimed, then contesting opponent, then central control.
        s = 0
        if (nx, ny) in unT:
            s += 120
        if (nx, ny) in opT:
            s += 170
        if (nx, ny) in selfT:
            s -= 2
        # Move toward opponent territory boundary and overall center.
        s += -2 * (abs(nx - ox) + abs(ny - oy))
        s += -abs(nx - cx) - abs(ny - cy)
        # Slightly prefer reducing distance to nearest unclaimed/opponent if far.
        if unT:
            tx, ty = min(unT, key=lambda p: abs(p[0] - nx) + abs(p[1] - ny))
            s += -0.7 * (abs(tx - nx) + abs(ty - ny))
        if opT:
            tx, ty = min(opT, key=lambda p: abs(p[0] - nx) + abs(p[1] - ny))
            s += 0.6 * (abs(tx - nx) + abs(ty - ny)) * (-1)
        return s

    best_dx, best_dy = 0, 0
    best = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        v = score(nx, ny)
        if v > best:
            best = v
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]