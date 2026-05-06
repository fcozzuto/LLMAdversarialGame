def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def fallback():
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = man(nx, ny, ox, oy) * 2 - man(nx, ny, cx, cy) * 0.5
            if best is None or v > bestv or (v == bestv and (nx, ny) < best):
                best, bestv = (nx, ny), v
        if best is None:
            return [0, 0]
        return [best[0] - sx, best[1] - sy]

    if not resources:
        return fallback()

    best_t = None
    bestv = None
    for rx, ry in resources:
        d_me = man(sx, sy, rx, ry)
        d_op = man(ox, oy, rx, ry)
        center_bias = -0.08 * man(rx, ry, cx, cy)
        # Prefer targets we're closer to; also prefer those far from opponent.
        v = (d_op - d_me) * 2.2 - d_me * 0.9 + center_bias
        if best_t is None or v > bestv or (v == bestv and (rx, ry) < best_t):
            best_t, bestv = (rx, ry), v

    tx, ty = best_t

    # Step toward target while optionally increasing distance from opponent if tied.
    best_step = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dm = man(nx, ny, tx, ty)
        do = man(nx, ny, ox, oy)
        v = -dm * 3.0 + do * 0.6  # reduce distance to target primarily
        if best_score is None or v > best_score or (v == best_score and (dx, dy) < best_step):
            best_score = v
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]