def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def pick_target(px, py):
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = r[0], r[1]
            if not ok(rx, ry):
                continue
            ds = man(px, py, rx, ry)
            do = man(ox, oy, rx, ry)
            # Want to be earlier than opponent; if not possible, prefer smallest ds (fast points).
            pri = (do - ds, -ds, -((rx + ry) & 1), rx, ry)
            if best is None or pri > best:
                best = pri
        return best

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (None, -10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        t = pick_target(nx, ny)
        if t is None:
            continue
        do_minus_ds, neg_ds, parity, rx, ry = t
        # One-step advantage, plus small preference to reduce distance to the chosen target.
        val = do_minus_ds * 100 - (-neg_ds) * 2 + parity
        # Extra bias: move toward center to avoid being swept by row/col patterns.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        val += int(6 - (abs(nx - cx) + abs(ny - cy)))
        if val > best_move[1]:
            best_move = ((dx, dy), val)

    if best_move[0] is None:
        return [0, 0]
    return [best_move[0][0], best_move[0][1]]