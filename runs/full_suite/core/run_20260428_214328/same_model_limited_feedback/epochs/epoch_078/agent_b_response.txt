def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])
    cx = (w - 1) / 2.0; cy = (h - 1) / 2.0

    def cheb(a, b, c, d):
        dx = a - c; dy = b - d
        return dx * dx + dy * dy

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    # Choose a resource where we are likely to arrive earlier (by Chebyshev distance squared)
    best = None
    best_gain = -10**18
    for rx, ry in resources:
        du = max(abs(sx - rx), abs(sy - ry))
        dop = max(abs(ox - rx), abs(oy - ry))
        gain = dop - du
        if gain > best_gain:
            best_gain = gain
            best = (rx, ry)

    if best is None:
        tx, ty = cx, cy
    else:
        tx, ty = best[0], best[1]

    deltas = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Evaluate candidate moves: move closer to target; also try to increase opponent's distance to that target
    def move_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx = sx + dx; ny = sy + dy
        if not move_ok(nx, ny):
            continue
        # target distance uses squared Euclidean to keep simple/deterministic
        dist_u = cheb(nx, ny, tx, ty)
        dist_o = cheb(ox, oy, tx, ty)
        # prefer closer to target; and if both chase same target, prefer moves that push us to finish earlier
        # Use approximate "arrival advantage" after move
        du2 = max(abs(nx - tx), abs(ny - ty)) if best is not None else abs(nx - tx) + abs(ny - ty)
        dop2 = max(abs(ox - tx), abs(oy - ty)) if best is not None else abs(ox - tx) + abs(oy - ty)
        advantage = (dop2 - du2) if best is not None else 0.0
        val = (-dist_u) + 0.35 * advantage + 0.01 * (dist_o - cheb(ox, oy, tx, ty))
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move