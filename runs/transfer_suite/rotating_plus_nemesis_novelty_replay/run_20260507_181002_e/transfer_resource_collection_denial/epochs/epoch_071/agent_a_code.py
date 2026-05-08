def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a target resource that we can reach no later than opponent; prefer biggest advantage.
    best_t = None
    best_adv = None
    fallback_t = None
    fallback_d = None
    for tx, ty in res:
        ds = dist(sx, sy, tx, ty)
        do = dist(ox, oy, tx, ty)
        if fallback_t is None or ds < fallback_d:
            fallback_t, fallback_d = (tx, ty), ds
        if ds <= do:
            adv = (do - ds) * 2 - ds  # more advantage and closer
            if best_t is None or adv > best_adv:
                best_t, best_adv = (tx, ty), adv

    tx, ty = best_t if best_t is not None else fallback_t

    if (sx, sy) == (tx, ty):
        return [0, 0]

    # Choose move that reduces our distance to target and, secondarily, increases opponent distance to that same target.
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        d_s = dist(nx, ny, tx, ty)
        d_o = dist(ox, oy, tx, ty)
        # tie-break with resource closeness to prevent oscillation
        d_r = d_s
        score = (-d_s * 1000) + (d_o - d_s) * 10 - d_r
        if best_score is None or score > best_score:
            best_score, best = score, [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]