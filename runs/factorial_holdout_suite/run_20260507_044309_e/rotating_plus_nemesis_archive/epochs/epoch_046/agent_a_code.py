def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b is None or len(b) < 2:
            continue
        bx, by = int(b[0]), int(b[1])
        if 0 <= bx < w and 0 <= by < h:
            blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r is None or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
            resources.append((rx, ry))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def is_valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if (sx, sy) in resources:
        return [0, 0]
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer closer resources; if opponent closer, prefer still-closer-after-margin.
        key = (ds - min(do, ds) * 0.2, ds, -do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    cur_d = man(sx, sy, tx, ty)
    best_move = [0, 0]
    best_score = (cur_d, 1e9)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not is_valid(nx, ny):
            continue
        nd = man(nx, ny, tx, ty)
        # Small preference to reduce distance, then avoid stepping onto resources only if it doesn't help.
        score = (nd, abs(nx - tx) + abs(ny - ty))
        if score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move