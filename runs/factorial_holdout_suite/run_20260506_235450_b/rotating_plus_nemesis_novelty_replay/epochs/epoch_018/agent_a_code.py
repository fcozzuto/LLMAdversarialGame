def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Move to center-ish while staying safe
        tx, ty = (w - 1) // 2, (h - 1) // 2
        bestm, bestk = [0, 0], None
        for mx, my in cand:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            k = (abs(nx - tx) + abs(ny - ty)) + 0.001 * (abs(nx - ox) + abs(ny - oy))
            if bestk is None or k < bestk:
                bestk, bestm = k, [mx, my]
        return bestm

    def man(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    best_move = [0, 0]
    best_key = None

    for mx, my in cand:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Choose the resource that gives us the best distance advantage from this next cell.
        best_adv = None
        best_self_d = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer than opponent
            if best_adv is None or adv > best_adv or (adv == best_adv and sd < best_self_d):
                best_adv, best_self_d = adv, sd

        # Prefer stronger advantage; if tie, prefer shorter self distance; then keep closer to opponent (block).
        key = (best_adv, -best_self_d, -man(nx, ny, ox, oy), mx, my)
        if best_key is None or key > best_key:
            best_key, best_move = key, [mx, my]

    return best_move