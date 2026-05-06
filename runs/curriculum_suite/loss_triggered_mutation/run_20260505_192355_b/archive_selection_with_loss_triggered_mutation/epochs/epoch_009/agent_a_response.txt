def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = None
    best_key = None
    if res:
        res_sorted = sorted(res)
        for tx, ty in res_sorted:
            myd = md(sx, sy, tx, ty)
            opd = md(ox, oy, tx, ty)
            # Prefer where we're closer than opponent (larger advantage), then closer overall.
            key = (-(opd - myd), myd, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                target = (tx, ty)

    if target is None:
        tx, ty = (w - 1 if w > 0 else 0, h - 1 if h > 0 else 0)
        if (tx, ty) in obst:
            tx, ty = 0, 0
        target = (tx, ty)

    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            d_after = md(nx, ny, tx, ty)
            # Also lightly prefer moving away from opponent to reduce contesting.
            d_opp_after = md(nx, ny, ox, oy)
            candidates.append((d_after, -d_opp_after, dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    candidates.sort()
    _, _, dx, dy, _, _ = candidates[0]
    return [int(dx), int(dy)]