def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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
    if not resources:
        resources = [(ox, oy)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def adj_obs(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in obstacles:
                        c += 1
        return c

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Choose resource that maximizes our advantage (opp distance - our distance)
        # Add a small tie-breaker to prefer closer resources and safer positions.
        best_adv_for_move = None
        for tx, ty in resources:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            adv = od - sd
            key = (adv, -sd, -abs(tx - nx) - abs(ty - ny), -tx, -ty)
            if best_adv_for_move is None or key > best_adv_for_move[0]:
                best_adv_for_move = (key, tx, ty, sd, od)

        adv_key, tx, ty, sd, od = best_adv_for_move
        # If we're not improving (adv small), bias toward blocking near opponent/resource line.
        line_block = -(man(nx, ny, ox, oy) > 0 and man(nx, ny, tx, ty) > man(sx, sy, tx, ty))

        score = (adv_key[0] * 1000) + (adv_key[1] * 10) + (-sd) + (-(adj_obs(nx, ny)) * 3) + line_block
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score:
            # deterministic tie-break: prefer moves that reduce distance to best target
            if best is not None:
                bx, by = best
                curd_best = man(sx + bx, sy + by, tx, ty)
                newd = sd
                if newd < curd_best:
                    best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]