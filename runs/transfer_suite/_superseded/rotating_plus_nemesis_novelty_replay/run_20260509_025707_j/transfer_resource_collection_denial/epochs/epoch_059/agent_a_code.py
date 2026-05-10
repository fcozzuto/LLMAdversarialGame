def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        # deterministic fallback: drift to center-ish
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Precompute obstacle-free resource targets
    targets = []
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        targets.append((rx, ry))
    if not targets:
        return [0, 0]

    best_move = [0, 0]
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Evaluate move by best "denial-robust" target
        # score = (opp_d - sd) + bias for immediate closeness and denying opponent access
        move_best = None
        for rx, ry in targets:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # If we're as good as or better, prioritize faster capture; otherwise deny by targeting resources with large opponent advantage.
            adv = od - sd
            key = (adv, -sd, od, -(sd + max(0, od - sd)))
            if move_best is None or key > move_best:
                move_best = key

        if move_best is None:
            continue

        # Add deterministic tie-break: prefer moves with larger x then y (fixed order already, but keep explicit)
        final_key = (move_best[0], move_best[1], move_best[2], move_best[3], dx, dy)
        if best_key is None or final_key > best_key:
            best_key = final_key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]