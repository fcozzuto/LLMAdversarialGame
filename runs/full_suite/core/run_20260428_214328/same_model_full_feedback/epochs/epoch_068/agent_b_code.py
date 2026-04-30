def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    if not resources:
        best = (10**9, 10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_to_opp = man(nx, ny, ox, oy)
            # Prefer moving away from opponent, then center-ish
            center = -((nx - (w - 1) / 2) ** 2 + (ny - (h - 1) / 2) ** 2)
            cand = (0 - d_to_opp, 0 - center, abs(dx) + abs(dy), nx, ny)
            if cand < best:
                best = cand
        return [best[3] - sx, best[4] - sy] if best[4] != 0 else [0, 0]

    # Pick a target that is good for us: low myDist and high oppDist (compete)
    best_target = None
    best_key = None
    for tx, ty in resources:
        md = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # Key: lower is better
        key = (md - 0.85 * od, md, -od, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (tx, ty)

    tx, ty = best_target
    # Move step that most reduces distance to target while not suiciding into obstacles
    best_move = (10**9, 10**9, 10**9, 0, 0)  # (dist_to_target, -dist_to_opp, step_cost, nx, ny)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist_t = man(nx, ny, tx, ty)
        dist_o = man(nx, ny, ox, oy)
        step_cost = abs(dx) + abs(dy)
        cand = (dist_t, -dist_o, step_cost, nx, ny)
        if cand < best_move:
            best_move = cand

    nx, ny = best_move[3], best_move[4]
    return [nx - sx, ny - sy]