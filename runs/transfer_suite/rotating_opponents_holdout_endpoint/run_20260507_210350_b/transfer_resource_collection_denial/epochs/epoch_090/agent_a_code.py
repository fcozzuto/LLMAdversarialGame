def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def king(a, b, c, d):
        return max(abs(a - c), abs(b - d))

    opp_best = min(resources, key=lambda t: (king(ox, oy, t[0], t[1]), t[0], t[1]))

    best_t = None
    best_val = -10**9
    for t in resources:
        myd = king(sx, sy, t[0], t[1])
        opd = king(ox, oy, t[0], t[1])
        # Prefer stealing tempo from opponent; deprioritize their most-likely target.
        depr = 1 if t == opp_best else 0
        val = (opd - myd) - 0.2 * depr - 0.01 * myd
        if val > best_val + 1e-12:
            best_val = val
            best_t = t
        elif abs(val - best_val) <= 1e-12 and (myd < king(sx, sy, best_t[0], best_t[1]) if best_t else True):
            best_t = t

    tx, ty = best_t
    dx_options = [-1, 0, 1]
    candidates = []
    for dx in dx_options:
        for dy in dx_options:
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, king(nx, ny, tx, ty), king(nx, ny, ox, oy)))
    if not candidates:
        return [0, 0]

    # If we can match distance to target quicker than opponent, prioritize that; otherwise approach target.
    candidates.sort(key=lambda it: (-1 * ((king(sx + it[0], sy + it[1], tx, ty) <= king(sx, sy, tx, ty)) ), it[2], it[3], it[0], it[1]))
    return [int(candidates[0][0]), int(candidates[0][1])]