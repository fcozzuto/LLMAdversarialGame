def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if safe(nx, ny):
                c += 1
        return c

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or role.endswith("e")
    is_pursuer = ("pursuer" in role) or role.endswith("p")
    if not (is_evader or is_pursuer):
        is_pursuer = True

    if is_evader:
        # Maximize distance from pursuer while keeping good mobility and avoiding dead-ends.
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not safe(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            m = mobility(nx, ny)
            # Prefer breaking distance ties by moving toward farthest corner deterministically.
            corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
            far_corner = max(corners, key=lambda c: abs(nx - c[0]) + abs(ny - c[1]))
            corner_bias = abs(nx - far_corner[0]) + abs(ny - far_corner[1])
            val = (d, m, corner_bias, -abs(nx - sx) - abs(ny - sy))
            if bestv is None or val > bestv:
                bestv = val
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Pursuer: greedy step toward opponent with obstacle-aware tie breaks.
    # If multiple equally good, choose one that maximizes mobility and reduces risk of getting boxed.
    if sx == ox and sy == oy:
        return [0, 0]

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        m = mobility(nx, ny)
        # Penalize moves that keep opponent about same distance but reduce mobility.
        val = (-dist, m, -max(0, 6 - (m + 1)), -abs(nx - sx) - abs(ny - sy))
        if bestv is None or val > bestv:
            bestv = val
            best = (dx, dy)
    return [best[0], best[1]] if best is not None else [0, 0]