def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        my_rem = observation.get("remaining_resource_count", None)
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            myd = man((sx, sy), (rx, ry))
            opd = man((ox, oy), (rx, ry))
            # Prefer resources we can reach sooner; tie-break by position hash.
            score = (myd - opd) * 1000 + (myd) + ((rx * 131 + ry * 17) % 97) * 0.001
            if best is None or score < best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = w // 2, h // 2

    best_move = (10**18, (0, 0))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        myd = abs(nx - tx) + abs(ny - ty)
        opd = abs(nx - ox) + abs(ny - oy)
        # Also discourage moving onto/near opponent to reduce contesting risk.
        val = myd * 10 - opd
        if val < best_move[0]:
            best_move = (val, (dx, dy))

    return [int(best_move[1][0]), int(best_move[1][1])]