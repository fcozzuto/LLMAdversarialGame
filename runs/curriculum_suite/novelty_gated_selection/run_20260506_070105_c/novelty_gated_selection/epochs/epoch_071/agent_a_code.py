def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    if not resources:
        # deterministic fallback: drift away from opponent toward center
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        cand = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
        for dxx, dyy in cand:
            nx, ny = sx + dxx, sy + dyy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dxx, dyy]
        return [0, 0]

    # Pick best target with preference for "we can get it first"
    best_t = None
    best_val = None
    for tx, ty in resources:
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        edge = 1 if (tx == 0 or tx == w - 1 or ty == 0 or ty == h - 1) else 0
        # lower is better: favor ds << do; also avoid very close to opponent
        val = ds * 3 - do * 4 + edge * 1 + (1 if ds == 0 else 0) * (-2)
        if best_val is None or val < best_val:
            best_val, best_t = val, (tx, ty)

    tx, ty = best_t

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    # Heuristic: move that reduces our distance to target, while also steering away from opponent if tied
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds1 = man(nx, ny, tx, ty)
        do1 = man(nx, ny, ox, oy)
        opp_to_t = man(ox, oy, tx, ty)
        step_gain = (man(sx, sy, tx, ty) - ds1)
        # prefer taking/approaching, discourage getting too close to opponent
        score = -step_gain * 10 + ds1 * 1 - (min(do1, 8) * 0.2) + (1 if man(ox, oy, nx, ny) <= 1 else 0) * 1.5 + (opp_to_t == 0) * 5
        if best_score is None or score < best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]