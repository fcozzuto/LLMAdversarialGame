def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position", None) or [w - 1, h - 1]
    op = observation.get("opponent_position", None) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obst_adj_pen(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            nx = x + ddx
            if nx < 0 or nx >= w:
                continue
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ny = y + ddy
                if ny < 0 or ny >= h:
                    continue
                if (nx, ny) in obstacles:
                    c += 1
        return c

    # Choose a target resource we can win for (closer than opponent) if possible.
    turn = int(observation.get("turn_index", 0) or 0)
    best_t = None
    best_key = None
    for (rx, ry) in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we are relatively closer to; if tie, prefer nearer overall.
        # Small deterministic bias via turn and coordinates to break ties.
        delta = ds - do
        # Strongly prefer "we are not worse" resources
        winish = 0 if delta <= 0 else 1
        key = (winish, delta, ds, obst_adj_pen(rx, ry), (rx * 11 + ry * 7 + turn) % 1000, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Evaluate next step: minimize (distance-to-target, obstacle penalty, distance-to-opponent to deny races).
    best_move = None
    best_eval = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_op = cheb(nx, ny, ox, oy)
        # If we move onto a square adjacent to obstacles, discourage it to avoid repeated hits.
        pen = obst_adj_pen(nx, ny)
        # Deterministic tie-break: prefer certain geometric directions based on turn parity.
        dir_bias = 0
        if (dx, dy) == (-1, 0) or (dx, dy) == (0, -1):
            dir_bias = 1 if (turn % 2 == 0) else 0
        if (dx, dy) == (1, 0) or (dx, dy) == (0, 1):
            dir_bias = 0 if (turn % 2 == 0) else 1
        eval_key = (d_to_t, pen, -d_to_op, dir_bias, (nx * 13 + ny * 3 + turn) % 1000, dx, dy)
        if best_eval is None or eval_key < best_eval