def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cd(a, b, c, d):
        ax, ay, bx, by = a, b, c, d
        return max(abs(ax - bx), abs(ay - by))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                ok = True
            ok = in_bounds(nx, ny) and (nx, ny) not in obstacles
            if ok:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            myd = cd(sx, sy, rx, ry)
            opd = cd(ox, oy, rx, ry)
            adv = opd - myd
            key = (adv, -myd)  # prioritize where we're closer by margin
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx, ry)
    else:
        best_r = None

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not in_bounds(nx, ny):
            return -10**9
        s = 0.0
        if best_r is not None:
            rx, ry = best_r
            myd = cd(nx, ny, rx, ry)
            s += 50.0 / (1 + myd)  # closer to target
        # Safety and spacing vs opponent
        opd = cd(nx, ny, ox, oy)
        s += 0.8 * opd
        # Mild anti-oscillation: prefer moves that reduce distance to target when possible
        if best_r is not None:
            cur = cd(sx, sy, best_r[0], best_r[1])
            nxt = cd(nx, ny, best_r[0], best_r[1])
            s += 0.15 * (cur - nxt)
        return s

    best = None
    best_s = None
    for dx, dy in moves:
        sc = score_move(dx, dy)
        if best_s is None or sc > best_s:
            best_s = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]