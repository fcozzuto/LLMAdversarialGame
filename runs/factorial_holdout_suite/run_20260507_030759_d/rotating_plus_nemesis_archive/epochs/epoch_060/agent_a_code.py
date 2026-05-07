def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds
        pr = 0 if ds < do else 1
        # Bias to contest when opponent is "sweeping": target resources in/near opponent row
        row_bias = 0
        if ry == oy: row_bias = -0
        elif abs(ry - oy) == 1: row_bias = 0
        else: row_bias = 1
        key = (pr + row_bias, -lead, ds, -do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # Candidate moves: prefer direct toward target; deterministic tie-break order
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for dx, dy in [(dx0, dy0), (dx0, 0), (0, dy0), (dx0, -dy0), (-dx0, dy0), (0, 0),
                    (1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]:
        if dx < -1 or dx > 1 or dy < -1 or dy > 1:
            continue
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        candidates.append((dx, dy))

    if not candidates:
        return [0, 0]

    def dist_to_target(x, y):
        return cheb(x, y, tx, ty)

    best_move = None
    best_md = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        md = dist_to_target(nx, ny)
        # Deterministic order when equal: lowest dx, then lowest dy
        key = (md, dx, dy)
        if best_md is None or key < best_md:
            best_md = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]