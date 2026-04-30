def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # If no resources: drift toward center while avoiding getting closer to opponent too easily.
    if not resources:
        tx, ty = w // 2, h // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = -man(nx, ny, tx, ty) + 0.2 * man(nx, ny, ox, oy)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Evaluate each move by the best resource we could secure next.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        local_best = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Primary: win distance; Secondary: come sooner if likely uncontested; Tertiary: avoid moving toward opponent.
            win = (do - ds)
            contest_pen = 0
            if do <= ds + 1:
                contest_pen = 0.75 * (ds - do)  # penalize when opponent is not slower
            # Prefer closer resources if we are winning; otherwise prefer to reduce opponent access.
            access = 0.12 * (do - ds)
            score = win + access + contest_pen - 0.06 * man(nx, ny, ox, oy)
            if score > local_best:
                local_best = score

        # Slight tie-break: prefer moves that increase distance to opponent when scores are equal.
        final_score = local_best + 0.001 * man(nx, ny, ox, oy)
        if final_score > best_score:
            best_score = final_score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]