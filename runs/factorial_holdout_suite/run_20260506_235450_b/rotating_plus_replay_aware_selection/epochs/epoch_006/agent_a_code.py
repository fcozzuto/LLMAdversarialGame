def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        # drift to center to reduce blocking by obstacles
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in legal:
            d = man(nx, ny, tx, ty)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Choose best resource by estimated advantage and urgency.
    best_res = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # prioritize resources where we are closer; break ties by being closer overall
        # and by keeping some distance from the opponent (if nearly tied).
        adv = do - ds
        key = (adv, -ds, -(man(rx, ry, sx, sy) == 0), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)
    rx, ry = best_res

    # Evaluate each move: primarily move toward chosen resource; if tied, prefer
    # moves that deny opponent by increasing their distance to our target.
    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        ds_next = man(nx, ny, rx, ry)
        # approximate opponent next distance if we move and they likely chase; still deterministic
        # without exact opponent move, we use current direction heuristic.
        step_ox = 0 if ox == rx else (1 if rx > ox else -1)
        step_oy = 0 if oy == ry else (1 if ry > oy else -1)
        o1x, o1y = ox + step_ox, oy + step_oy
        if inb(o1x, o1y) and (o1x, o1y) not in obstacles:
            do_next = man(o1x, o1y, rx, ry)
        else:
            do_next = man(ox, oy, rx, ry)
        # score higher is better
        score = (-(ds_next), (do_next - ds_next), -((nx - rx) == 0 and (ny - ry) == 0) , -abs(nx - ox) - abs(ny - oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]