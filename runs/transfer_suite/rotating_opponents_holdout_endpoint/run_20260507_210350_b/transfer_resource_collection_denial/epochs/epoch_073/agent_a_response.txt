def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_for_state(px, py):
        best = None
        for x, y in resources:
            sd = md(px, py, x, y)
            od = md(ox, oy, x, y)
            # Prefer resources where we are closer than opponent (large positive advantage).
            adv = od - sd
            # Secondary: prefer nearer target to reduce risk of losing tempo.
            key = (adv, -sd, -(x + y) % 2)
            if best is None or key > best[0]:
                best = (key, x, y, sd, od)
        return best[1], best[2], best[3], best[4]

    tx, ty, _, _ = best_for_state(sx, sy)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                ok = True
            else:
                ok = (0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles)
            if ok:
                candidates.append((dx, dy))

    # Prefer moves that increase our contest advantage to the current best target,
    # with a fallback to any move that yields a globally better target.
    cur_tx, cur_ty, cur_sd, cur_od = best_for_state(sx, sy)
    cur_adv = cur_od - cur_sd
    best_move = None
    best_key = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        ntx, nty, nsd, nod = best_for_state(nx, ny)
        nadv = nod - nsd
        # Primary: maximize advantage; Secondary: minimize distance to our selected best target; Tertiary: avoid no-op unless best.
        d_to_cur = md(nx, ny, cur_tx, cur_ty)
        key = (nadv - cur_adv, nadv, -d_to_cur, -(dx == 0 and dy == 0))
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move