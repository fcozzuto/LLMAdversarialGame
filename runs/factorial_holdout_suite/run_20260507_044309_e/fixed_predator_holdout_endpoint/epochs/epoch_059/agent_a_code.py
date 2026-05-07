def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles", None) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                blocked.add((px, py))

    resources = []
    for r in (observation.get("resources", None) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd  # positive => we are closer
        # If both are equal, prefer nearer to deny future turns
        key = (adv, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    cx = tx - sx
    cy = ty - sy
    step_x = 0 if cx == 0 else (1 if cx > 0 else -1)
    step_y = 0 if cy == 0 else (1 if cy > 0 else -1)

    candidates = []
    for dx, dy in [(step_x, step_y), (step_x, 0), (0, step_y), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            candidates.append((dx, dy))
    if not candidates:
        return [0, 0]

    # Choose move that reduces our distance most; break ties by improving advantage vs opponent
    best_mv = None
    best_mv_key = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        cur_sd = md(nx, ny, tx, ty)
        cur_od = md(ox, oy, tx, ty)
        mv_key = (-cur_sd, cur_od - cur_sd, -dx, -dy)
        if best_mv_key is None or mv_key > best_mv_key:
            best_mv_key = mv_key
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]