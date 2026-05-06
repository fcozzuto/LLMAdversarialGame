def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obs = set()
    for o in (observation.get("obstacles") or []):
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
        elif isinstance(o, dict):
            x, y = o.get("x"), o.get("y")
        else:
            continue
        if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
        elif isinstance(r, dict):
            x, y = r.get("x"), r.get("y")
        else:
            continue
        if isinstance(x, int) and isinstance(y, int) and inb(x, y):
            res.append((x, y))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if res:
        best = None
        for tx, ty in res:
            ds = md(sx, sy, tx, ty)
            do = md(ox, oy, tx, ty)
            # Prefer targets we are closer to; slight tie-break for being closer to center.
            s = (do - ds) * 10 - ds - (abs(tx - cx) + abs(ty - cy)) * 0.1
            if best is None or s > best[0]:
                best = (s, tx, ty)
        _, tx, ty = best
        # Greedy one-step toward the target.
        bestm = None
        for dx, dy, nx, ny in moves:
            cur = md(nx, ny, tx, ty) - md(ox, oy, tx, ty) * 0.02
            if bestm is None or cur < bestm[0]:
                bestm = (cur, dx, dy)
        return [bestm[1], bestm[2]]

    # Fallback: move toward center, but avoid moving closer to opponent if possible.
    bestm = None
    for dx, dy, nx, ny in moves:
        score = (abs(nx - cx) + abs(ny - cy)) + (0.3 * md(nx, ny, ox, oy))
        if bestm is None or score < bestm[0]:
            bestm = (score, dx, dy)
    return [bestm[1], bestm[2]]