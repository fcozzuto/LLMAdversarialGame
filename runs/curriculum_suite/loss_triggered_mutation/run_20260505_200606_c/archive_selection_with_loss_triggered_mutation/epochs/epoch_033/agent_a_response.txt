def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    opp_next = set()
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if ok(nx, ny):
            opp_next.add((nx, ny))

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                d = md(nx, ny, tx, ty)
                key = (d, dx, dy)
                if best is None or key < best[0]:
                    best = (key, dx, dy)
        return [best[1], best[2]]

    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # Strongly prefer resources we can beat; next prefer short/near-mid and good in our quadrant.
        beat = 1 if ds <= do else 0
        key = (-(beat), ds - do, ds + 0.15 * do, abs((rx - sx) * (rx - ox)) + abs((ry - sy) * (ry - oy)))
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = md(nx, ny, rx, ry)
        # Avoid stepping into opponent's next-step neighborhood when contesting this target.
        step_conflict = 1 if (nx, ny) in opp_next else 0
        # If we are on same row/col band as target, prefer it (helps against sweep-like behavior).
        band = 1 if (ny == ry or nx == rx) else 0
        key = (d + 2.5 * step_conflict - 0.4 * band, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]