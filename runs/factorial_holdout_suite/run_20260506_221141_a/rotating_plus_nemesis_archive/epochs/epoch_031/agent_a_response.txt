def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources_raw = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []

    if not isinstance(sx, int) or not isinstance(sy, int) or not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    for tx, ty in resources:
        my_d = man(sx, sy, tx, ty)
        op_d = man(ox, oy, tx, ty)
        margin = op_d - my_d  # positive means we are faster
        # Small preference to keep some line ahead (avoid going to cells closer to opponent than us)
        penalty = 0
        if my_d > op_d:
            penalty = 2
        # Prefer closer among equal margins
        key = (-margin, penalty, my_d, (tx + ty))
        if best is None or key < best[0]:
            best = (key, tx, ty)

    _, tx, ty = best

    def step_towards(cx, cy, tx, ty):
        dx = 0 if tx == cx else (1 if tx > cx else -1)
        dy = 0 if ty == cy else (1 if ty > cy else -1)
        return dx, dy

    def try_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if -1 <= dx <= 1 and -1 <= dy <= 1 and 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [dx, dy]
        return None

    dx0, dy0 = step_towards(sx, sy, tx, ty)
    cand = []
    cand.append((dx0, dy0))
    # Deterministic fallback order: prioritize x then y, then stay
    cand.append((dx0, 0))
    cand.append((0, dy0))
    cand.append((-dx0, dy0))
    cand.append((dx0, -dy0))
    cand.append((0, 0))

    for dx, dy in cand:
        res = try_move(dx, dy)
        if res is not None:
            return res

    return [0, 0]