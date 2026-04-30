def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    obs_set = {tuple(p) for p in obstacles}
    resources = observation["resources"]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            nx = clamp(nx, 0, w - 1)
            ny = clamp(ny, 0, h - 1)
            if (nx, ny) in obs_set:
                continue
            cand.append((dx, dy, nx, ny))

    if not cand:
        cand = [(0, 0, sx, sy)]

    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            dk = dist((sx, sy), (rx, ry)) - 0.85 * dist((ox, oy), (rx, ry))
            if best_key is None or dk < best_key:
                best_key = dk
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_val = None
    for dx, dy, nx, ny in cand:
        d_self = dist((nx, ny), (tx, ty))
        d_opp = dist((ox, oy), (tx, ty))
        # prefer moves that keep pressure on the chosen target and widen opponent distance
        # also slightly penalize getting closer to opponent directly (deny without collision chasing)
        val = -d_self + 0.35 * (d_opp - dist((ox, oy), (nx, ny))) + 0.08 * dist((nx, ny), (ox, oy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]