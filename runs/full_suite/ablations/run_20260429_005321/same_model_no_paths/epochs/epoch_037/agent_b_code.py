def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Target selection: favor resources where we are ahead; otherwise pick least-bad.
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            ahead = do - ds
            # Prefer positive ahead; break ties by smaller ds then lexicographic.
            key = (-ahead, ds, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (w // 2, h // 2)

    # Greedy step toward target while avoiding obstacles.
    dx = 0
    dy = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    def step_score(nx, ny):
        # Lower is better: reduce distance to target, and keep away from opponent if tied.
        d_to = dist(nx, ny, tx, ty)
        d_op = dist(nx, ny, ox, oy)
        return (d_to, -d_op, abs(nx - tx) + abs(ny - ty), nx, ny)

    # Try ideal move first; if blocked, search among legal neighbors deterministically.
    cand = (sx + dx, sy + dy)
    if ok(cand[0], cand[1]):
        return [dx, dy]

    best_move = (0, 0)
    best_sc = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not ok(nx, ny):
            continue
        sc = step_score(nx, ny)
        if best_sc is None or sc < best_sc:
            best_sc = sc
            best_move = (mx, my)
    return [int(best_move[0]), int(best_move[1])]