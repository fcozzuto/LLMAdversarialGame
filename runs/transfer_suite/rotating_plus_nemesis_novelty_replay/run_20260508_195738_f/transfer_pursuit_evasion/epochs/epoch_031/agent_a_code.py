def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = (observation.get("self_role", "") or "").lower()
    evader = role == "evader"

    res = observation.get("resources", []) or []
    remaining = observation.get("remaining_resource_count", None)
    use_res = True
    if remaining is not None:
        try:
            use_res = int(remaining) > 0
        except Exception:
            use_res = True

    resources = []
    if isinstance(res, (list, tuple)):
        for r in res:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                x, y = int(r[0]), int(r[1])
                if 0 <= x < w and 0 <= y < h:
                    resources.append((x, y))

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    if use_res and resources:
        tx, ty = min(resources, key=lambda p: dist2(sx, sy, p[0], p[1]))
    else:
        tx, ty = ox, oy

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_op = dist2(nx, ny, ox, oy)
        d_t = dist2(nx, ny, tx, ty)
        # If evader, maximize distance to opponent; otherwise minimize.
        v = (d_op if evader else -d_op) + (-d_t // 2)
        if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]