def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    for tx, ty in resources:
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        # Prefer: where opponent is slower; then closer to self; then favor cells with smaller "corner distance"
        corner_bias = (tx <= 1) * 10 + (ty <= 1) * 6 + (tx >= w - 2) * 4 + (ty >= h - 2) * 3
        key = (do - ds, -ds, -corner_bias, -tx, -ty)
        if best is None or key > best[0]:
            best = (key, tx, ty)

    _, tx, ty = best

    # Choose step toward target; if blocked, try alternative axis step (still deterministic).
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    def valid(npx, npy):
        return 0 <= npx < w and 0 <= npy < h and (npx, npy) not in obstacles

    cands = []
    # primary: diagonal/axis toward target
    cands.append((sx + dx, sy + dy))
    # alternatives: axis-first
    cands.append((sx + dx, sy))
    cands.append((sx, sy + dy))
    # fallback: stay if all else blocked
    cands.append((sx, sy))

    # If some candidates are obstacle-blocked, filter but keep a deterministic fallback.
    for nx, ny in cands:
        if valid(nx, ny):
            return [nx - sx, ny - sy]

    return [0, 0]