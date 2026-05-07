def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        a = dx if dx >= 0 else -dx
        b = dy if dy >= 0 else -dy
        return a if a > b else b

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def best_score(px, py):
        if not resources:
            return (-10**9, 10**9, 0)
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = r[0], r[1]
            if not (isinstance(rx, int) and isinstance(ry, int) and inb(rx, ry)):
                continue
            dme = cheb(px, py, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            margin = dop - dme
            # prefer winning immediately (positive margin), then closer, then toward top-left deterministically
            key = (margin, -dme, -(rx * 9 + ry))
            if best is None or key > best:
                best = key
        if best is None:
            return (-10**9, 10**9, 0)
        return best

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        key = best_score(nx, ny)
        # tie-break: prefer moves that keep closer to some resource (implicitly via -dme), then smaller dx,dy
        tieb = (key, -(dx * dx + dy * dy), -dx, -dy)
        if best_key is None or tieb > best_key:
            best_key = tieb
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]