def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = corners[0]
        best = None
        for c in corners:
            v = md(ox, oy, c[0], c[1]) - 0.01 * md(sx, sy, c[0], c[1])
            if best is None or v > best:
                best = v
                tx, ty = c
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    res = resources
    best_move = [0, 0]
    best_val = None
    best_t = None

    def best_target_value(px, py):
        bt = None
        btv = None
        for rx, ry in res:
            ds = md(px, py, rx, ry)
            do = md(ox, oy, rx, ry)
            # Bias against "sweep_rows": prefer targets that require breaking our row/col next.
            align_bonus = 0.6 if (px == rx or py == ry) else 0.0
            v = (do - ds) * 10.0 - ds + align_bonus
            if btv is None or v > btv:
                btv = v
                bt = (rx, ry)
        return btv, bt

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        v, t = best_target_value(nx, ny)
        # Tie-break: closer to target, then lexicographic move
        if best_val is None or v > best_val or (v == best_val and (md(nx, ny, t[0], t[1]), dx, dy) < (md(sx, sy, best_t[0], best_t[1]), best_move[0], best_move[1])):
            best_val = v
            best_move = [dx, dy]
            best_t = t

    return [int(best_move[0]), int(best_move[1])]