def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def best_target():
        if not resources:
            return (sx, sy)
        best = None
        best_val = -10**9
        for rx, ry in resources:
            myd = dist((sx, sy), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            if myd == 0:
                val = 10**9
            else:
                # Prefer resources where opponent is relatively farther; also prefer closer overall.
                val = (opd - myd) * 10 - myd
            if (myd == 0) or (val > best_val):
                best_val = val
                best = (rx, ry)
        return best if best is not None else (sx, sy)

    tx, ty = best_target()

    # Candidate move deltas (including stay), deterministic preference order
    deltas = []
    dx = 0
    dy = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    # Start with direct step towards target, then try alternatives
    primary = (dx, dy)
    candidates = [primary]
    for ddy in (-1, 0, 1):
        for ddx in (-1, 0, 1):
            if (ddx, ddy) == primary:
                continue
            candidates.append((ddx, ddy))
    candidates.append((0, 0))

    # Evaluate candidates by: reachability, distance to target, and keep away from opponent slightly
    best_move = (0, 0)
    best_score = -10**9
    for ddx, ddy in candidates:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue
        myd = abs(nx - tx) + abs(ny - ty)
        opd = abs(nx - ox) + abs(ny - oy)
        # If opponent is near, avoid positions that let them capture immediately
        # (roughly maximize opponent distance while minimizing myd)
        score = -myd * 20 + opd
        # Tie-break deterministically
        score += (0 if (ddx, ddy) == primary else -1)
        if score > best_score:
            best_score = score
            best_move = (ddx, ddy)

    return [int(best_move[0]), int(best_move[1])]