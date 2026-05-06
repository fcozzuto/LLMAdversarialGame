def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        # Deterministic fallback: drift toward center to avoid corner stagnation.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -man(nx, ny, cx, cy)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Interception-focused: pick a resource where we improve our competitive position,
        # but strongly penalize moves that let the opponent keep an advantage.
        local = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # If we can be no slower, reward margin; otherwise penalize being behind.
            if sd <= od:
                v = 8 + (od - sd) * 2 - sd * 0.12
            else:
                v = -(sd - od) * 2 - sd * 0.08

            # Encourage moving toward resources that the opponent is currently closest to,
            # even if not yet winnable, to enable future contest.
            v += 0.25 * (12 - od)

            if v > local:
                local = v

        # Small anti-oscillation bias toward moves that reduce distance to the chosen best resource.
        # Deterministic: approximate by using the minimum self distance after this move.
        mind = min(man(nx, ny, rx, ry) for rx, ry in resources)
        local -= mind * 0.01

        if local > best_val:
            best_val, best_move = local, (dx, dy)

    return [best_move[0], best_move[1]]