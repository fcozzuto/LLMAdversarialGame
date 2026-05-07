def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", None) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in (observation.get("resources", None) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    # Prefer resources we can reach first; if none, still maximize advantage.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        adv = od - sd
        # tie-break: closer to we being denied, and prefer more "dominant" cells
        key = (adv, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # First try greedy move toward target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    cand = (sx + dx, sy + dy)
    if cand[0] == sx + dx and cand[1] == sy + dy and 0 <= cand[0] < w and 0 <= cand[1] < h and cand not in obstacles:
        return [dx, dy]

    # Otherwise pick best feasible step (deterministic) that reduces our distance most.
    best_step = None
    best_step_key = None
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = dist((nx, ny), (tx, ty))
        nod = dist((ox, oy), (tx, ty))
        adv = nod - nsd
        step_key = (adv, -nsd, ddx, ddy)
        if best_step_key is None or step_key > best_step_key:
            best_step_key = step_key
            best_step = (ddx, ddy)

    return [int(best_step[0]), int(best_step[1])]