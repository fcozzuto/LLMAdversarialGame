def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_r = None
    best_key = None
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        d_me = md(sx, sy, rx, ry)
        d_opp = md(ox, oy, rx, ry)
        if d_me == 0:
            continue
        # Prefer where we can beat opponent by a margin; avoid resources they can snatch immediately.
        margin = d_opp - d_me
        prox_pen = 900 if d_opp <= 2 else (200 if d_opp <= 3 else 0)
        behind_pen = 50 if d_me > d_opp else 0
        center_bias = 0.02 * (abs(rx - cx) + abs(ry - cy))
        key = (prox_pen + behind_pen + center_bias - margin, d_me, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        # Fallback: head to nearest valid resource, else stay.
        best_r = None
        best_key = None
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry):
                continue
            d = md(sx, sy, rx, ry)
            key = (d, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        if best_r is None:
            return [0, 0]

    tx, ty = best_r
    # Local greedy step toward target with deterministic obstacle-avoidance.
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = md(nx, ny, tx, ty)
        # Slightly prefer moves that also keep distance from opponent to reduce interference.
        oppd = md(nx, ny, ox, oy)
        mkey = (d, -oppd, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]