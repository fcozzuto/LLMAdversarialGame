def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    res_set = set(tuple(p) for p in resources)

    def clamp(x, a, b):
        return a if x < a else b if x > b else x

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    # Pick a resource where we are at least competitive (earlier than opponent), otherwise closest overall.
    best = None
    best_key = None
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # Prefer: we can arrive not much later; then closer to us; then deterministic tie-break by position.
        key = (d_self - 0.55 * d_opp, d_self, rx, ry)
        if best is None or key < best_key:
            best, best_key = (rx, ry), key

    tx, ty = best if best is not None else (sx, sy)

    # Choose move that goes toward target while avoiding obstacles; reward immediate collection.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, tx, ty)
        collect = 1.0 if (nx, ny) in res_set else 0.0
        # Minor preference to reduce distance to opponent if equally good (helps contest resources indirectly).
        opp_dist = cheb(nx, ny, ox, oy)
        score = (-dist, -collect, opp_dist, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]