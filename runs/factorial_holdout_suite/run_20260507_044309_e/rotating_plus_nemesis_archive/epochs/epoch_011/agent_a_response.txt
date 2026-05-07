def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = -md((nx, ny), (cx, cy))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_target = None
    best_tv = -10**18
    for tx, ty in resources:
        d_s = md((sx, sy), (tx, ty))
        d_o = md((ox, oy), (tx, ty))
        center_bias = -md((tx, ty), (cx, cy)) * 0.02
        # Prefer resources we are much closer to; slight preference for central ones.
        tv = (d_o - d_s) * 10.0 + center_bias
        if tv > best_tv:
            best_tv = tv
            best_target = (tx, ty)

    tx, ty = best_target
    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_s_next = md((nx, ny), (tx, ty))
        d_o_to_target = md((ox, oy), (tx, ty))
        # Encourage getting to target faster than opponent; also avoid wandering.
        v = (d_o_to_target - d_s_next) * 10.0 - d_s_next * 0.3 - md((nx, ny), (cx, cy)) * 0.02
        # If we are adjacent, prefer moves that reduce opponent pressure on other resources indirectly:
        # deterministic small tie-break toward staying closer to target.
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best