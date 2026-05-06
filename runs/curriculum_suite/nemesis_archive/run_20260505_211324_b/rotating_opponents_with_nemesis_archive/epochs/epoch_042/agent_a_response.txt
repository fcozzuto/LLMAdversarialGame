def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_key = None
    for tx, ty in res:
        sd = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        gap = od - sd  # positive means we are faster
        # If opponent is closer, we prefer a target where we are as little behind as possible,
        # but still prioritize potentially-denying targets (big gap), and avoid far-away thrash.
        # Tie-break deterministically by coordinates.
        key = (
            -(gap),                # prefer larger gap (we faster) -> smaller negative
            sd,                    # then smaller our distance
            od,                    # then smaller opponent distance
            tx, ty
        )
        # Convert to "max" by inverting logic via comparison to current best_key.
        # We'll pick the resource with minimum ( -gap, sd, od, tx, ty ) by using key directly.
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
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

    # Micro-adjust to avoid moving into an obstacle if possible (deterministic).
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obs:
        # Try axis moves as alternatives, prefer diagonal still if safe.
        cand = []
        cand.append((dx, 0))
        cand.append((0, dy))
        cand.append((dx, dy))
        cand.append((0, 0))
        for cdx, cdy in cand:
            ax, ay = sx + cdx, sy + cdy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obs:
                return [cdx, cdy]
        return [0, 0]

    return [dx, dy]