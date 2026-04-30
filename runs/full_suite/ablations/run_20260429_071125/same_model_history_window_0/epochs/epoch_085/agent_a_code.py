def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        dx = -dx if dx < 0 else dx
        dy = -dy if dy < 0 else dy
        return dx + dy

    def step_good(nx, ny, tx, ty):
        if not inb(nx, ny) or (nx, ny) in obs:
            return None
        myd = dist((nx, ny), (tx, ty))
        opd = dist((ox, oy), (tx, ty))
        score = myd - 0.35 * opd
        if (nx, ny) in res_set:
            score -= 3.0
        return score

    res_set = set((x, y) for x, y in resources)
    if not res_set:
        return [0, 0]

    best = None
    best_val = None
    for rx, ry in res_set:
        myd = dist((sx, sy), (rx, ry))
        opd = dist((ox, oy), (rx, ry))
        # Deny/priority: prefer resources where we are closer than opponent
        val = (opd - myd) * 2.0 - 0.15 * myd
        if best is None or val > best_val or (val == best_val and (rx, ry) < best):
            best = (rx, ry)
            best_val = val

    tx, ty = best
    cur_step = step_good(sx, sy, tx, ty)
    best_move = (0, 0)
    best_score = cur_step if cur_step is not None else 1e9

    # Deterministic greedy toward target, with slight tie-breaking via resource denial
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        sc = step_good(nx, ny, tx, ty)
        if sc is None:
            continue
        if sc < best_score:
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]