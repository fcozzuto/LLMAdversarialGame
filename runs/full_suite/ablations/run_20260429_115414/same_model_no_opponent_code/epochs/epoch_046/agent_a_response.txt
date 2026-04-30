def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort(key=lambda t: (t[0], t[1]))  # deterministic tie-break

    if resources:
        best_move = (0, 0)
        best_val = -10**18
        best_d = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            my_best = None
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Advantage: larger means resource likely to be ours first
                adv = opd - myd
                # Prefer faster take if advantage equal
                val = adv * 1000 - myd
                if my_best is None or val > my_best[0] or (val == my_best[0] and myd < my_best[1]):
                    my_best = (val, myd)
            val, myd = my_best if my_best is not None else (-10**12, 10**9)
            if val > best_val or (val == best_val and myd < best_d):
                best_val = val
                best_d = myd
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: drift toward center while avoiding obstacles
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_d = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, cx, cy)
        if d < best_d:
            best_d = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]